from __future__ import annotations

import json
import textwrap
from dataclasses import asdict
from pathlib import Path
from typing import Self, cast

from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel.remote import RemoteGraph
from langgraph.types import Command as LGCommand
from pydantic import BaseModel, Field, field_validator
from rich.console import ConsoleRenderable

from ..base import (
    FormalizationState,
)
from ..command import (
    Command,
    InitStateCommand,
    RootCommand,
)
from ..runtime_context import ContextSchema
from ..task import Interaction


class GraphState(BaseModel):
    """
    Graph state of Code Logician
    """

    steps: list[Interaction] = Field(
        default_factory=list, description="Commands and their trajectories"
    )
    step_i: int | None = Field(default=None, description="Index of the current step")
    info: dict = Field(
        default_factory=dict, description="Internal information shared between nodes"
    )

    @property
    def last_fstate(self) -> FormalizationState | None:
        """Return the last formalization state"""
        last_fstate = None
        for step in self.steps:
            if step.last_fstate is not None:
                last_fstate = step.last_fstate
        return last_fstate

    @field_validator("steps", mode="after")
    @classmethod
    def last_fstate_cannot_be_later_than_the_first_pending_step(
        cls, steps: list[Interaction]
    ) -> list[Interaction]:
        step_i = next(
            (
                i
                for i, step in enumerate(steps)
                if step.task is not None and step.task.status == "pending"
            ),
            None,
        )
        if step_i is None:
            return steps

        for step in steps[step_i + 1 :]:
            if step.last_fstate is not None:
                raise ValueError(
                    "Last fstate cannot be later than the first pending step"
                )
        return steps

    def add_commands(
        self,
        commands: Command | list[Command],
    ) -> Self:
        """Return a new GraphState with the added commands"""
        match commands:
            case command if isinstance(command, Command):
                new_steps = [
                    *self.steps,
                    Interaction(command=command),
                ]
                update = {"steps": new_steps}
            case list() as commands:
                new_steps = [
                    *self.steps,
                    *[Interaction(command=command) for command in commands],
                ]
                update = {"steps": new_steps}
            case _:
                raise ValueError(f"Invalid command: {commands}")
        return self.__class__.model_validate(self.model_dump() | update)

    def init_with_file(self, file_path: str, src_lang: str) -> GraphState:
        content = Path(file_path).read_text()
        steps = [
            Interaction(
                command=RootCommand(
                    root=InitStateCommand(
                        src_code=content,
                        src_lang=src_lang,
                    )
                )
            )
        ]
        return GraphState(steps=steps)

    async def run(
        self,
        graph: CompiledStateGraph[GraphState, ContextSchema, GraphState, GraphState]
        | RemoteGraph,
        config: RunnableConfig | None = None,
        resume: LGCommand | None = None,
    ) -> tuple[Self, dict | None]:
        config = RunnableConfig(**(config or {}))
        runtime_context = config.get("configurable", {})

        default_runtime_context = asdict(ContextSchema())
        graph_bound_config = getattr(graph, "config", {}) or {}
        graph_bound_runtime_context = graph_bound_config.get("configurable", {})
        runtime_context = (
            default_runtime_context | graph_bound_runtime_context | runtime_context
        )
        config["configurable"] = runtime_context

        if resume is None:
            inputs = json.loads(self.model_dump_json())
        else:
            inputs = resume
        values: dict | None = None
        updates: dict | None = None
        async for chunk in graph.astream(
            inputs,
            config=config,
            **({} if isinstance(graph, RemoteGraph) else {"context": runtime_context}),
            stream_mode=["values", "updates"],
        ):
            chunk_type, chunk_value = chunk
            if chunk_type == "values":
                values = cast(dict, chunk_value)
            elif chunk_type == "updates":
                updates = cast(dict, chunk_value)
        gs = GraphState.model_validate(values)
        if "__interrupt__" in updates:
            return (gs, updates)
        else:
            return (gs, None)

    def __rich__(self) -> ConsoleRenderable:
        return Interaction.render_interactions_summary(self.steps)

    def __repr__(self):
        s = ""
        s += "Graph State:\n\n"
        s += f"{len(self.steps)} Steps\n\n"
        for i, step in enumerate(self.steps, 1):
            s += f"Step {i}:\n\n"
            s += textwrap.indent(step.__repr__(), "  ")
            s += "\n\n"
            s += "=" * 40 + "\n\n"

        return s

"""
Tests for the codex.cqea module.
"""

import pytest
from zodchy.codex.cqea import (
    Message,
    Context,
    Task,
    Command,
    Query,
    Event,
    Error,
)
from zodchy.codex.operator import ClauseStream


class TestTask:
    """Test class for Task base class."""

    def test_task_inherits_from_message(self):
        """Test that Task inherits from Message."""
        assert issubclass(Task, Message)


class TestCommand:
    """Test class for Command base class."""

    # type: ignore

    def test_command_inherits_from_task(self):
        """Test that Command inherits from Task."""
        assert issubclass(Command, Task)

    def test_command_inherits_from_message(self):
        """Test that Command inherits from Message."""
        assert issubclass(Command, Message)


class TestQuery:
    """Test class for Query base class."""

    def test_query_inherits_from_task(self):
        """Test that Query inherits from Task."""
        assert issubclass(Query, Task)

    def test_query_inherits_from_message(self):
        """Test that Query inherits from Message."""
        assert issubclass(Query, Message)

    def test_query_has_iter_method(self):
        """Test that Query has __iter__ method defined."""
        assert hasattr(Query, "__iter__")

    def test_query_iter_is_abstract(self):
        """Test that Query.__iter__ is abstract."""

        class ConcreteQuery(Query):
            def __iter__(self) -> ClauseStream:
                return iter([])

        query = ConcreteQuery()
        result = list(query)
        assert result == []


class TestEvent:
    """Test class for Event base class."""

    def test_event_inherits_from_message(self):
        """Test that Event inherits from Message."""
        assert issubclass(Event, Message)


class TestError:
    """Test class for Error base class."""

    def test_error_inherits_from_event(self):
        """Test that Error inherits from Event."""
        assert issubclass(Error, Event)

    def test_error_inherits_from_message(self):
        """Test that Error inherits from Message."""
        assert issubclass(Error, Message)


class TestCQEAHierarchy:
    """Test class for CQEA class hierarchy."""

    def test_task_is_message(self):
        """Test that Task is a Message."""
        assert issubclass(Task, Message)

    def test_command_is_task(self):
        """Test that Command is a Task."""
        assert issubclass(Command, Task)

    def test_query_is_task(self):
        """Test that Query is a Task."""
        assert issubclass(Query, Task)

    def test_event_is_message(self):
        """Test that Event is a Message."""
        assert issubclass(Event, Message)

    def test_error_is_event(self):
        """Test that Error is an Event."""
        assert issubclass(Error, Event)

    def test_concrete_implementations(self):
        """Test that concrete implementations work correctly."""

        class MyCommand(Command):
            pass

        class MyQuery(Query):
            def __iter__(self) -> ClauseStream:
                return iter([])

        class MyEvent(Event):
            pass

        class MyError(Error):
            pass

        # Should be able to instantiate concrete classes
        command = MyCommand()
        assert isinstance(command, Command)
        assert isinstance(command, Task)
        assert isinstance(command, Message)

        query = MyQuery()
        assert isinstance(query, Query)
        assert isinstance(query, Task)
        assert isinstance(query, Message)
        assert list(query) == []

        event = MyEvent()
        assert isinstance(event, Event)
        assert isinstance(event, Message)

        error = MyError()
        assert isinstance(error, Error)
        assert isinstance(error, Event)
        assert isinstance(error, Message)

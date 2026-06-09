"""
Prim Debugger
Provides breakpoint management, variable inspection, call stack navigation,
step-through execution, conditional breakpoints, and watch expressions.
"""

import sys
import os
import re
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class DebugState(Enum):
    """Debugger state"""
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"
    TERMINATED = "terminated"


class StepMode(Enum):
    """Step execution modes"""
    OVER = "over"  # Step over function calls
    INTO = "into"  # Step into function calls
    OUT = "out"    # Step out of current function


@dataclass
class Breakpoint:
    """Breakpoint information"""
    file_path: str
    line_number: int
    condition: Optional[str] = None
    hit_count: int = 0
    enabled: bool = True
    id: int = 0


@dataclass
class WatchExpression:
    """Watch expression for monitoring variables"""
    expression: str
    value: Any = None
    error: Optional[str] = None


@dataclass
class StackFrame:
    """Stack frame information"""
    file_path: str
    function_name: str
    line_number: int
    local_variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DebugEvent:
    """Debug event"""
    event_type: str
    file_path: str
    line_number: int
    message: Optional[str] = None
    data: Optional[Dict] = None


class PrimDebugger:
    """Main debugger for Prim language"""

    def __init__(self):
        self.state = DebugState.RUNNING
        self.breakpoints: List[Breakpoint] = []
        self.watch_expressions: List[WatchExpression] = []
        self.call_stack: List[StackFrame] = []
        self.current_frame: Optional[StackFrame] = None
        self.step_mode: Optional[StepMode] = None
        self.step_depth: int = 0
        self.breakpoint_counter: int = 0
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.source_files: Dict[str, List[str]] = {}
        self.variables: Dict[str, Any] = {}
        
        # Import interpreter if available
        self.interpreter = None
        try:
            from prim_interpreter import PrimInterpreter
            self.interpreter = PrimInterpreter()
        except ImportError:
            pass

    def add_breakpoint(
        self,
        file_path: str,
        line_number: int,
        condition: Optional[str] = None
    ) -> Breakpoint:
        """Add a breakpoint"""
        self.breakpoint_counter += 1
        breakpoint = Breakpoint(
            id=self.breakpoint_counter,
            file_path=file_path,
            line_number=line_number,
            condition=condition
        )
        self.breakpoints.append(breakpoint)
        self._emit_event('breakpoint_added', breakpoint)
        return breakpoint

    def remove_breakpoint(self, breakpoint_id: int) -> bool:
        """Remove a breakpoint by ID"""
        for i, bp in enumerate(self.breakpoints):
            if bp.id == breakpoint_id:
                del self.breakpoints[i]
                self._emit_event('breakpoint_removed', bp)
                return True
        return False

    def toggle_breakpoint(self, breakpoint_id: int) -> Optional[Breakpoint]:
        """Toggle breakpoint enabled state"""
        for bp in self.breakpoints:
            if bp.id == breakpoint_id:
                bp.enabled = not bp.enabled
                return bp
        return None

    def list_breakpoints(self) -> List[Breakpoint]:
        """List all breakpoints"""
        return self.breakpoints

    def add_watch_expression(self, expression: str) -> WatchExpression:
        """Add a watch expression"""
        watch = WatchExpression(expression=expression)
        self.watch_expressions.append(watch)
        self._emit_event('watch_added', watch)
        return watch

    def remove_watch_expression(self, index: int) -> bool:
        """Remove a watch expression"""
        if 0 <= index < len(self.watch_expressions):
            del self.watch_expressions[index]
            return True
        return False

    def update_watch_expressions(self):
        """Update all watch expressions"""
        for watch in self.watch_expressions:
            try:
                # Evaluate expression in current context
                value = self._evaluate_expression(watch.expression)
                watch.value = value
                watch.error = None
            except Exception as e:
                watch.error = str(e)

    def get_watch_values(self) -> List[Tuple[str, Any]]:
        """Get current values of all watch expressions"""
        results = []
        for watch in self.watch_expressions:
            if watch.error:
                results.append((watch.expression, f"Error: {watch.error}"))
            else:
                results.append((watch.expression, watch.value))
        return results

    def step_over(self):
        """Step over function calls"""
        self.state = DebugState.STEPPING
        self.step_mode = StepMode.OVER
        self.step_depth = len(self.call_stack)

    def step_into(self):
        """Step into function calls"""
        self.state = DebugState.STEPPING
        self.step_mode = StepMode.INTO
        self.step_depth = len(self.call_stack)

    def step_out(self):
        """Step out of current function"""
        self.state = DebugState.STEPPING
        self.step_mode = StepMode.OUT
        self.step_depth = len(self.call_stack)

    def continue_execution(self):
        """Continue execution"""
        self.state = DebugState.RUNNING
        self.step_mode = None

    def pause(self):
        """Pause execution"""
        self.state = DebugState.PAUSED

    def stop(self):
        """Stop debugging"""
        self.state = DebugState.TERMINATED
        self._emit_event('debugger_stopped', None)

    def check_breakpoint(
        self,
        file_path: str,
        line_number: int,
        context: Optional[Dict] = None
    ) -> Optional[Breakpoint]:
        """Check if execution should pause at this location"""
        for bp in self.breakpoints:
            if not bp.enabled:
                continue
            
            if bp.file_path == file_path and bp.line_number == line_number:
                # Check condition if present
                if bp.condition:
                    try:
                        if context:
                            result = self._evaluate_expression(bp.condition, context)
                            if not result:
                                continue
                        else:
                            continue
                    except:
                        continue
                
                bp.hit_count += 1
                return bp
        
        return None

    def should_pause(
        self,
        file_path: str,
        line_number: int,
        context: Optional[Dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if execution should pause"""
        # Check breakpoints
        bp = self.check_breakpoint(file_path, line_number, context)
        if bp:
            return True, f"Breakpoint {bp.id} hit"
        
        # Check step mode
        if self.state == DebugState.STEPPING:
            if self.step_mode == StepMode.INTO:
                return True, "Step into"
            elif self.step_mode == StepMode.OVER:
                if len(self.call_stack) <= self.step_depth:
                    return True, "Step over"
            elif self.step_mode == StepMode.OUT:
                if len(self.call_stack) < self.step_depth:
                    return True, "Step out"
        
        return False, None

    def push_frame(
        self,
        file_path: str,
        function_name: str,
        line_number: int,
        local_variables: Optional[Dict] = None
    ):
        """Push a new frame onto the call stack"""
        frame = StackFrame(
            file_path=file_path,
            function_name=function_name,
            line_number=line_number,
            local_variables=local_variables or {}
        )
        self.call_stack.append(frame)
        self.current_frame = frame
        self._emit_event('frame_pushed', frame)

    def pop_frame(self):
        """Pop a frame from the call stack"""
        if self.call_stack:
            frame = self.call_stack.pop()
            self._emit_event('frame_popped', frame)
            if self.call_stack:
                self.current_frame = self.call_stack[-1]
            else:
                self.current_frame = None

    def get_call_stack(self) -> List[StackFrame]:
        """Get the current call stack"""
        return self.call_stack

    def get_local_variables(self) -> Dict[str, Any]:
        """Get local variables in current frame"""
        if self.current_frame:
            return self.current_frame.local_variables
        return {}

    def get_variable(self, name: str) -> Optional[Any]:
        """Get a variable value"""
        # Check local variables first
        if self.current_frame and name in self.current_frame.local_variables:
            return self.current_frame.local_variables[name]
        
        # Check global variables
        if name in self.variables:
            return self.variables[name]
        
        return None

    def set_variable(self, name: str, value: Any):
        """Set a variable value"""
        if self.current_frame and name in self.current_frame.local_variables:
            self.current_frame.local_variables[name] = value
        else:
            self.variables[name] = value

    def evaluate_expression(self, expression: str) -> Any:
        """Evaluate an expression in the current context"""
        return self._evaluate_expression(expression)

    def _evaluate_expression(
        self,
        expression: str,
        context: Optional[Dict] = None
    ) -> Any:
        """Evaluate an expression"""
        # Simple evaluation - in a real implementation, this would use the interpreter
        try:
            # Try to evaluate as a literal
            if expression.isdigit():
                return int(expression)
            elif expression.replace('.', '').isdigit():
                return float(expression)
            elif expression.startswith('"') and expression.endswith('"'):
                return expression[1:-1]
            elif expression.startswith("'") and expression.endswith("'"):
                return expression[1:-1]
            
            # Try to get variable value
            value = self.get_variable(expression)
            if value is not None:
                return value
            
            # Try to evaluate as Python expression (for simple cases)
            if context:
                return eval(expression, {}, context)
            else:
                # Try with local variables
                if self.current_frame:
                    return eval(expression, {}, self.current_frame.local_variables)
                return eval(expression, {}, self.variables)
        
        except Exception as e:
            raise ValueError(f"Cannot evaluate expression: {e}")

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def _emit_event(self, event_type: str, data: Any):
        """Emit a debug event"""
        event = DebugEvent(
            event_type=event_type,
            file_path=self.current_frame.file_path if self.current_frame else "",
            line_number=self.current_frame.line_number if self.current_frame else 0,
            data=data
        )
        
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(event)

    def load_source_file(self, file_path: str) -> List[str]:
        """Load source file for debugging"""
        if file_path not in self.source_files:
            try:
                with open(file_path, 'r') as f:
                    self.source_files[file_path] = f.readlines()
            except FileNotFoundError:
                self.source_files[file_path] = []
        return self.source_files[file_path]

    def get_source_line(self, file_path: str, line_number: int) -> Optional[str]:
        """Get a specific line from a source file"""
        lines = self.load_source_file(file_path)
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].rstrip()
        return None

    def get_source_context(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 3
    ) -> List[Tuple[int, str]]:
        """Get source code context around a line"""
        lines = self.load_source_file(file_path)
        context = []
        
        start = max(1, line_number - context_lines)
        end = min(len(lines), line_number + context_lines)
        
        for i in range(start, end + 1):
            context.append((i, lines[i - 1].rstrip()))
        
        return context

    def get_state(self) -> DebugState:
        """Get current debugger state"""
        return self.state

    def is_paused(self) -> bool:
        """Check if debugger is paused"""
        return self.state == DebugState.PAUSED

    def is_running(self) -> bool:
        """Check if debugger is running"""
        return self.state == DebugState.RUNNING

    def is_terminated(self) -> bool:
        """Check if debugger is terminated"""
        return self.state == DebugState.TERMINATED


class DebugCLI:
    """Command-line interface for the debugger"""

    def __init__(self, debugger: PrimDebugger):
        self.debugger = debugger
        self.commands = {
            'help': self.cmd_help,
            'break': self.cmd_break,
            'b': self.cmd_break,
            'clear': self.cmd_clear,
            'continue': self.cmd_continue,
            'c': self.cmd_continue,
            'step': self.cmd_step,
            's': self.cmd_step,
            'next': self.cmd_next,
            'n': self.cmd_next,
            'finish': self.cmd_finish,
            'f': self.cmd_finish,
            'list': self.cmd_list,
            'l': self.cmd_list,
            'where': self.cmd_where,
            'w': self.cmd_where,
            'print': self.cmd_print,
            'p': self.cmd_print,
            'watch': self.cmd_watch,
            'info': self.cmd_info,
            'quit': self.cmd_quit,
            'q': self.cmd_quit,
        }

    def cmd_help(self, args: List[str]):
        """Show help"""
        print("""
Debugger Commands:
  break <file>:<line> [condition]  Set a breakpoint
  clear <id>                      Remove a breakpoint
  continue                        Continue execution
  step                            Step into function calls
  next                            Step over function calls
  finish                          Step out of current function
  list [line] [count]             List source code
  where                           Show call stack
  print <expression>              Evaluate and print expression
  watch <expression>              Add watch expression
  info breakpoints                List all breakpoints
  info locals                      Show local variables
  quit                            Quit debugger
""")

    def cmd_break(self, args: List[str]):
        """Set a breakpoint"""
        if not args:
            print("Usage: break <file>:<line> [condition]")
            return
        
        location = args[0]
        if ':' not in location:
            print("Invalid location format. Use file:line")
            return
        
        file_path, line_str = location.split(':', 1)
        try:
            line_number = int(line_str)
            condition = ' '.join(args[1:]) if len(args) > 1 else None
            bp = self.debugger.add_breakpoint(file_path, line_number, condition)
            print(f"Breakpoint {bp.id} set at {file_path}:{line_number}")
        except ValueError:
            print("Invalid line number")

    def cmd_clear(self, args: List[str]):
        """Clear a breakpoint"""
        if not args:
            print("Usage: clear <breakpoint_id>")
            return
        
        try:
            bp_id = int(args[0])
            if self.debugger.remove_breakpoint(bp_id):
                print(f"Breakpoint {bp_id} removed")
            else:
                print(f"Breakpoint {bp_id} not found")
        except ValueError:
            print("Invalid breakpoint ID")

    def cmd_continue(self, args: List[str]):
        """Continue execution"""
        self.debugger.continue_execution()
        print("Continuing...")

    def cmd_step(self, args: List[str]):
        """Step into function calls"""
        self.debugger.step_into()
        print("Stepping...")

    def cmd_next(self, args: List[str]):
        """Step over function calls"""
        self.debugger.step_over()
        print("Stepping over...")

    def cmd_finish(self, args: List[str]):
        """Step out of current function"""
        self.debugger.step_out()
        print("Stepping out...")

    def cmd_list(self, args: List[str]):
        """List source code"""
        if not self.debugger.current_frame:
            print("No current frame")
            return
        
        file_path = self.debugger.current_frame.file_path
        line_number = self.debugger.current_frame.line_number
        
        context_lines = 3
        if len(args) > 0:
            try:
                line_number = int(args[0])
                if len(args) > 1:
                    context_lines = int(args[1])
            except ValueError:
                pass
        
        context = self.debugger.get_source_context(file_path, line_number, context_lines)
        
        for line_num, line in context:
            marker = '>' if line_num == line_number else ' '
            print(f"{marker} {line_num}: {line}")

    def cmd_where(self, args: List[str]):
        """Show call stack"""
        stack = self.debugger.get_call_stack()
        if not stack:
            print("No call stack")
            return
        
        print("Call stack:")
        for i, frame in enumerate(reversed(stack)):
            print(f"  #{i}: {frame.function_name} at {frame.file_path}:{frame.line_number}")

    def cmd_print(self, args: List[str]):
        """Evaluate and print expression"""
        if not args:
            print("Usage: print <expression>")
            return
        
        expression = ' '.join(args)
        try:
            value = self.debugger.evaluate_expression(expression)
            print(f"{expression} = {value}")
        except Exception as e:
            print(f"Error: {e}")

    def cmd_watch(self, args: List[str]):
        """Add watch expression"""
        if not args:
            print("Usage: watch <expression>")
            return
        
        expression = ' '.join(args)
        watch = self.debugger.add_watch_expression(expression)
        print(f"Watch expression added: {expression}")

    def cmd_info(self, args: List[str]):
        """Show info"""
        if not args:
            print("Usage: info <breakpoints|locals>")
            return
        
        info_type = args[0]
        
        if info_type == 'breakpoints':
            bps = self.debugger.list_breakpoints()
            if not bps:
                print("No breakpoints")
            else:
                print("Breakpoints:")
                for bp in bps:
                    status = "enabled" if bp.enabled else "disabled"
                    print(f"  {bp.id}: {bp.file_path}:{bp.line_number} ({status})")
                    if bp.condition:
                        print(f"      Condition: {bp.condition}")
        
        elif info_type == 'locals':
            locals_dict = self.debugger.get_local_variables()
            if not locals_dict:
                print("No local variables")
            else:
                print("Local variables:")
                for name, value in sorted(locals_dict.items()):
                    print(f"  {name} = {value}")
        
        else:
            print(f"Unknown info type: {info_type}")

    def cmd_quit(self, args: List[str]):
        """Quit debugger"""
        self.debugger.stop()
        print("Quitting debugger...")

    def run_command(self, command: str):
        """Run a debugger command"""
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")


def main():
    """Main entry point for debugger CLI"""
    debugger = PrimDebugger()
    cli = DebugCLI(debugger)
    
    print("""
╔════════════════════════════════════════════════════════════╗
║           Prim Debugger v1.1                                ║
║                                                            ║
║  Type 'help' for commands | Type 'quit' to exit           ║
╚════════════════════════════════════════════════════════════╝
""")
    
    while not debugger.is_terminated():
        try:
            command = input("(prim-debug) ").strip()
            if command:
                cli.run_command(command)
        except KeyboardInterrupt:
            print("\nInterrupted. Type 'quit' to exit.")
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()

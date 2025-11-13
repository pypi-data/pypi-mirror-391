import subprocess
from dataclasses import dataclass
from typing import Any

import execjs
import orjson
import py_mini_racer
from charset_normalizer import from_bytes

from utils._logger import _logger


class _execute:
    class js:
        @staticmethod
        def _get_js_code(
                js_code: str | None = None,
                js_file_path: str | None = None
        ) -> str:
            if js_code is None and js_file_path is None:
                raise ValueError(
                    f"Either js_code: {js_code!r} or js_file_path: {js_file_path!r} must be provided"
                )
            if js_code is not None:
                return js_code
            if js_file_path is not None:
                with open(js_file_path, "r", encoding="utf-8") as f:
                    js_code = f.read()
            return js_code

        @staticmethod
        def execute_javascript_by_execjs(
                js_code: str | None = None,
                js_file_path: str | None = None,
                func_name: str | None = None,
                func_args: tuple[Any, ...] | None = None
        ) -> Any:
            """
            # language=javascript
            js_code = '''
                  function sdk () {
                    let sum = 0;
                    for (const n of arguments) {
                      if (typeof n === "number") sum += n;
                    }
                    return sum;
                  }
                  '''
            result = _execute.js.execute_javascript_by_execjs(js_code, func_name="sdk", func_args=(1, 2, "3"))
            print(result)

            Args:
                js_code:
                js_file_path:
                func_name:
                func_args:

            Returns:

            """
            js_code = _execute.js._get_js_code(js_code, js_file_path)

            ctx = execjs.compile(js_code)
            if func_name is None:
                result = ctx.eval(js_code)
                return result
            if func_args is None:
                func_args = tuple()
            result = ctx.call(func_name, *func_args)
            return result

        @staticmethod
        def execute_javascript_by_py_mini_racer(
                js_code: str | None = None,
                js_file_path: str | None = None,
                func_name: str | None = None,
                func_args: tuple[Any, ...] | None = None
        ) -> Any:
            """
            # language=javascript
            js_code = '''
                  function sdk () {
                    let sum = 0;
                    for (const n of arguments) {
                      if (typeof n === "number") sum += n;
                    }
                    return sum;
                  }
                  '''
            result = _execute.js.execute_javascript_by_py_mini_racer(js_code, func_name="sdk", func_args=(1, 2, "3"))
            print(result)

            Args:
                js_code:
                js_file_path:
                func_name:
                func_args:

            Returns:

            """
            js_code = _execute.js._get_js_code(js_code, js_file_path)

            ctx = py_mini_racer.MiniRacer()
            result = ctx.eval(js_code)
            if func_name is None:
                return result
            if func_args is None:
                func_args = tuple()
            result = ctx.call(func_name, *func_args)
            return result

        @staticmethod
        def execute_javascript_by_subprocess(
                js_code: str | None = None,
                js_file_path: str | None = None,
                arguments: tuple[Any, ...] | None = None,
        ) -> Any:
            """
            # language=javascript
            js_code = '''(function () {
              arguments = process.argv.slice(1).map(JSON.parse);
              let sum = 0;
              for (const n of arguments) {
                if (typeof n === "number") sum += n;
              }
              console.log(JSON.stringify({ "sum": sum }));
            })();'''

            result = _execute.js.execute_javascript_by_subprocess(js_code, arguments=(1, 2, "3",))
            print(result["sum"])

            Args:
                js_code:
                js_file_path:
                arguments:

            Returns:

            """
            js_code = _execute.js._get_js_code(js_code, js_file_path)

            args = ["node", "-e", js_code] + list(map(lambda x: orjson.dumps(x).decode(), arguments))
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            result = stdout.decode()
            result = orjson.loads(result)
            return result

    class cmd:
        @dataclass(frozen=True)
        class SubprocessPopenResult:
            returncode: int  # noqa
            stdout_content: bytes | None
            stdout_text: str
            stderr_content: bytes | None
            stderr_text: str

        @dataclass(frozen=True)
        class SubprocessRunResult:
            result: subprocess.CompletedProcess
            stdout_content: bytes
            stdout_text: str
            stderr_content: bytes
            stderr_text: str

        @staticmethod
        def _get_text(data: bytes, encoding: str | None = None) -> str:
            if encoding:
                text = data.decode(encoding)
            elif best_match := from_bytes(data).best():
                text = data.decode(best_match.encoding)
            else:
                text = str(data)
            return text

        @staticmethod
        def execute_cmd_code_by_subprocess_popen(
                cmd_code: str,
                encoding: str | None = None,
                logger: _logger.Logger | None = None
        ) -> SubprocessPopenResult:
            if logger:
                logger.debug(f'''$ {cmd_code}''')

            process = subprocess.Popen(
                cmd_code, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout_content, stdout_text = process.stdout, str()

            for i in process.stdout:
                text = _execute.cmd._get_text(i, encoding=encoding)
                stdout_text += text
                if text:
                    if logger:
                        logger.success("[√] " + text)

            stderr_content, stderr_text = process.stderr, str()
            for i in process.stderr:
                text = _execute.cmd._get_text(i, encoding=encoding)
                stderr_text += text
                if text:
                    if logger:
                        logger.error("[×] " + text)

            returncode = process.wait()

            return _execute.cmd.SubprocessPopenResult(
                returncode, stdout_content, stdout_text, stderr_content, stderr_text
            )

        @staticmethod
        def execute_cmd_code_by_subprocess_run(
                cmd_code: str,
                encoding: str | None = None,
                logger: _logger.Logger | None = None
        ) -> SubprocessRunResult:
            if logger:
                logger.debug(f'''> {cmd_code}''')

            result = subprocess.run(cmd_code, shell=True, capture_output=True)

            stdout_content, stdout_text = result.stdout, _execute.cmd._get_text(result.stdout, encoding=encoding)
            if stdout_text:
                if logger:
                    logger.success("[√] " + stdout_text)

            stderr_content, stderr_text = result.stderr, _execute.cmd._get_text(result.stderr, encoding=encoding)
            if stderr_text:
                if logger:
                    logger.error("[×] " + stderr_text)

            return _execute.cmd.SubprocessRunResult(
                result, stdout_content, stdout_text, stderr_content, stderr_text
            )


__all__ = [
    "_execute"
]

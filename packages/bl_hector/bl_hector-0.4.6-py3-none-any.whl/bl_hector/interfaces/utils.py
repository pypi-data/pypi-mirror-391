# Hector --- A collection manager.
# Copyright © 2023 Bioneland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from pypugjs.ext.jinja import Compiler, PyPugJSExtension
from pypugjs.parser import Parser
from pypugjs.utils import process


class PatchedCompiler(Compiler):  # type: ignore
    def visitInclude(self, node):  # type: ignore
        src, _, _ = self.options["loader"].get_source(
            self.options["environment"], self.format_path(node.path)
        )
        parser = Parser(src)
        block = parser.parse()
        return self.visit(block)


class PatchedPyPugJSExtension(PyPugJSExtension):  # type: ignore
    def preprocess(self, source, name, filename=None):  # type: ignore
        options = {
            "environment": self.environment,
            "loader": self.environment.loader,
        }

        return process(source, filename=name, compiler=PatchedCompiler, **options)

"""Write project-local library configuration with kiutils' LibTable serializer.

This is library registration, not CAD construction. MCP exposes no project
library-registration operation; pcbnew exposes no FP_LIB_TABLE Python class.
Run: uv run --with kiutils==1.4.8 python register_library.py
No shared/user library configuration or installed MCP dependency is changed.
"""
from pathlib import Path
from kiutils.libraries import LibTable,Library
ROOT=Path(__file__).resolve().parent
LibTable(type='fp_lib_table',libs=[Library(name='candidate',type='KiCad',uri='${KIPRJMOD}/candidate.pretty',description='FujiNet A500 R4 candidate-only footprints')]).to_file(str(ROOT/'fp-lib-table'))

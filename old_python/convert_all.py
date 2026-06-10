
import os
import re

def convert_py_to_prim(content, filename):
    # Add mode slim
    prim_content = ["#mode slim"]
    
    # Replace docstrings with comments
    content = re.sub(r'"""(.*?)"""', lambda m: "\n".join(["# " + line.strip() for line in m.group(1).strip().split("\n")]), content, flags=re.DOTALL)
    
    # Remove imports
    content = re.sub(r'^import .*', r'# \g<0>', content, flags=re.MULTILINE)
    content = re.sub(r'^from .* import .*', r'# \g<0>', content, flags=re.MULTILINE)
    
    # Handle Enums
    def replace_enum(match):
        enum_name = match.group(1)
        enum_body = match.group(2)
        constants = []
        for line in enum_body.strip().split("\n"):
            line = line.strip()
            if "=" in line:
                parts = line.split("=")
                name = parts[0].strip()
                val = parts[1].strip().split("#")[0].strip()
                constants.append(f"{enum_name}_{name} = {val}")
        return "\n".join(constants)
    
    content = re.sub(r'class (\w+)\(Enum\):(.*?)((?=class)|(?=def)|$)', replace_enum, content, flags=re.DOTALL)

    # Handle Dataclasses
    def replace_dataclass(match):
        class_name = match.group(1)
        fields_str = match.group(2)
        fields = []
        for line in fields_str.strip().split("\n"):
            line = line.strip()
            if ":" in line:
                name = line.split(":")[0].strip()
                fields.append(name)
        
        args = ", ".join(fields)
        dict_body = ", ".join([f'"{f}": {f}' for f in fields])
        return f"fn make_{class_name.lower()}({args}):\n    return {{{dict_body}}}"

    content = re.sub(r'@dataclass\s+class (\w+):(.*?)((?=class)|(?=def)|$)', replace_dataclass, content, flags=re.DOTALL)

    # Pre-process: Remove type hints (do this before method matching)
    content = re.sub(r':\s*[A-Z]\w+(\[.*?\])?', '', content)
    content = re.sub(r'->\s*[A-Z]\w+(\[.*?\])?', '', content)
    content = re.sub(r':\s*List\[.*?\]', '', content)
    content = re.sub(r':\s*Dict\[.*?\]', '', content)
    content = re.sub(r':\s*Optional\[.*?\]', '', content)
    content = re.sub(r':\s*Union\[.*?\]', '', content)
    content = re.sub(r':\s*Any', '', content)

    # Handle Classes and Methods
    current_class = None
    lines = content.split("\n")
    new_lines = []
    
    for line in lines:
        # Class definition (no indent)
        class_match = re.match(r'^class (\w+)(?:\(.*\))?:', line)
        if class_match:
            current_class = class_match.group(1)
            new_lines.append(f"# Class {current_class}")
            continue
            
        # Method definition (indented)
        method_match = re.match(r'^(\s+)def (\w+)\(self,?\s*(.*?)\):', line)
        if method_match:
            indent = method_match.group(1)
            method_name = method_match.group(2)
            args = method_match.group(3)
            
            if method_name == "__init__":
                new_fn_name = f"make_{current_class.lower()}" if current_class else "make_object"
                new_lines.append(f"{indent}fn {new_fn_name}({args}):")
                new_lines.append(f"{indent}    obj = {{}}")
            else:
                new_fn_name = f"{current_class.lower()}_{method_name}" if current_class else method_name
                full_args = "obj" + (", " + args if args else "")
                new_lines.append(f"{indent}fn {new_fn_name}({full_args}):")
            continue
            
        # Function definition (no indent)
        fn_match = re.match(r'^def (\w+)\((.*?)\):', line)
        if fn_match:
            fn_name = fn_match.group(1)
            args = fn_match.group(2)
            current_class = None # Reset class context for top-level functions
            new_lines.append(f"fn {fn_name}({args}):")
            continue

        # Indented function (not taking self)
        indented_fn_match = re.match(r'^(\s+)def (\w+)\((.*?)\):', line)
        if indented_fn_match:
            indent = indented_fn_match.group(1)
            fn_name = indented_fn_match.group(2)
            args = indented_fn_match.group(3)
            new_lines.append(f"{indent}fn {fn_name}({args}):")
            continue
            
        # self.attr -> obj["attr"]
        line = re.sub(r'self\.(\w+)', r'obj["\1"]', line)
        
        # self.method(...) -> class_method(obj, ...)
        if current_class:
            # Match self.method(args) -> class_method(obj, args)
            # This is tricky with nested calls, but we'll do a basic version
            line = re.sub(r'obj\["(\w+)"\]\((.*?)\)', lambda m: f"{current_class.lower()}_{m.group(1)}(obj, {m.group(2)})" if m.group(1) not in ["get", "pop", "items", "keys", "values"] else m.group(0), line)

        # list.append(item) -> list = push(list, item)
        line = re.sub(r'(\w+)\.append\((.*?)\)', r'\1 = push(\1, \2)', line)
        
        # dict.get(key) -> dict_get(dict, key)
        line = re.sub(r'(\w+)\.get\((.*?)\)', r'dict_get(\1, \2)', line)
        
        # None, True, False
        line = line.replace("None", "null").replace("True", "true").replace("False", "false")
        
        # f-strings (simplified)
        line = re.sub(r'f"(.*?)"', r'"\1"', line)
        
        new_lines.append(line)
        
    prim_content.extend(new_lines)
    return "\n".join(prim_content)

files_to_convert = [
    "prim_distributed_concurrency.py", "prim_distributed_runtime.py", "prim_distributed_storage.py",
    "prim_ffi.py", "prim_format.py", "prim_gc.py", "prim_generics.py", "prim_hal.py",
    "prim_hardware.py", "prim_http.py", "prim_interop.py", "prim_iot_protocols.py",
    "prim_jit.py", "prim_jit_extended.py", "prim_linter.py", "prim_low_level.py",
    "prim_low_level_programming.py", "prim_lsp_server.py", "prim_macros.py", "prim_math.py",
    "prim_memory_manager.py", "prim_memory_systems.py", "prim_microservices.py", "prim_mining.py",
    "prim_modules.py", "prim_optimization.py", "prim_os_integration.py", "prim_primitives.py",
    "prim_profiler.py", "prim_quantum_chemistry.py", "prim_quantum_cloud.py", "prim_quantum_control.py",
    "prim_quantum_crypto.py", "prim_quantum_finance.py", "prim_quantum_healthcare.py", "prim_quantum_hybrid.py",
    "prim_quantum_interface.py", "prim_quantum_libraries.py", "prim_quantum_library.py", "prim_quantum_logistics.py",
    "prim_quantum_networking.py", "prim_quantum_networks.py", "prim_quantum_optimization.py", "prim_quantum_qec.py",
    "prim_quantum_qml.py", "prim_quantum_science.py", "prim_quantum_security.py", "prim_quantum_simulation.py",
    "prim_quantum_tools.py", "prim_scientific.py", "prim_services.py", "prim_specification.py",
    "prim_stats.py", "prim_stm.py", "prim_test.py", "prim_training.py", "prim_type_checker.py",
    "prim_vision.py", "prim_visualization.py", "prim_std_collections.py", "prim_std_io.py",
    "prim_std_lib.py", "prim_std_math.py", "prim_std_strings.py", "prim_stdlib_docs.py"
]

# Track files that were already converted BEFORE we started
# (We don't want to overwrite manual conversions)
# Based on my first LS call:
pre_existing_prim = {
    "prim_actors_converted.prim", "prim_adaptive.prim", "prim_adts_converted.prim",
    "prim_architecture.prim", "prim_ast.prim", "prim_async_converted.prim",
    "prim_attention.prim", "prim_autonomous.prim", "prim_benchmarking_converted.prim",
    "prim_bigdata.prim", "prim_bio.prim", "prim_block_parser.prim", "prim_blockchain.prim",
    "prim_bootstrap.prim", "prim_bytecode.prim", "prim_channels.prim", "prim_cloud.prim",
    "prim_cloud_security.prim", "prim_cognitive.prim", "prim_compiler.prim",
    "prim_concurrency.prim", "prim_conscious.prim", "prim_consensus.prim",
    "prim_containers.prim", "prim_creative.prim", "prim_data.prim", "prim_database.prim",
    "prim_debugger.prim", "prim_deep_learning.prim", "prim_deployment.prim",
    "prim_deployment_integration.prim", "prim_devices.prim", "prim_devops.prim",
    "prim_diagnostics.prim", "prim_did.prim", "prim_doc_gen.prim", "prim_docs.prim",
    "prim_drivers.prim", "prim_ecosystem.prim", "prim_edge.prim", "prim_effects.prim",
    "prim_embedded.prim", "prim_emotional.prim", "prim_engineering.prim",
    "prim_error_context.prim", "prim_event_streaming.prim", "prim_fault_tolerance.prim",
    "prim_filesystems.prim", "prim_flow_parser.prim", "prim_industrial_iot.prim",
    "prim_interface.prim", "prim_interpreter.prim", "prim_iot.prim", "prim_iot_data.prim",
    "prim_kernel.prim", "prim_knowledge.prim", "prim_learning.prim", "prim_memory.prim",
    "prim_meta_cognition.prim", "prim_ml.prim", "prim_monitoring.prim",
    "prim_neuromorphic.prim", "prim_nlp.prim", "prim_os_security.prim", "prim_p2p.prim",
    "prim_package_manager.prim", "prim_parallel.prim", "prim_pattern_matching.prim",
    "prim_performance.prim", "prim_physics.prim", "prim_platforms.prim",
    "prim_predictive.prim", "prim_processes.prim", "prim_profiling.prim",
    "prim_reactive.prim", "prim_realtime.prim", "prim_realtime_concurrency.prim",
    "prim_realtime_systems.prim", "prim_reasoning.prim", "prim_registry.prim",
    "prim_repl.prim", "prim_research.prim", "prim_resource_management.prim",
    "prim_resources.prim", "prim_runtime.prim", "prim_scalability.prim",
    "prim_scheduling.prim", "prim_self_awareness.prim", "prim_self_evolution.prim",
    "prim_self_governance.prim", "prim_self_maintenance.prim", "prim_self_organization.prim",
    "prim_sensors.prim", "prim_serverless.prim", "prim_simulation.prim",
    "prim_slim_parser.prim", "prim_social.prim", "prim_timing.prim", "prim_tools.prim",
    "prim_wasm.prim", "prim_web.prim", "prim_web3.prim",
    "prim_std_collections.prim", "prim_std_io.prim", "prim_std_lib.prim",
    "prim_std_math.prim", "prim_std_strings.prim"
}

old_base_dir = r"d:\Aayan\codinglanguage\old_base"
src_dir = r"d:\Aayan\codinglanguage\src"
stdlib_dir = r"d:\Aayan\codinglanguage\stdlib"

def process_file(filename):
    py_path = os.path.join(old_base_dir, filename)
    if not os.path.exists(py_path):
        return
        
    prim_filename = filename.replace(".py", ".prim")
    
    # Decide target directory
    if filename.startswith("prim_std_") and filename != "prim_stdlib_docs.py":
        target_dir = stdlib_dir
    else:
        target_dir = src_dir
        
    prim_path = os.path.join(target_dir, prim_filename)
    
    # Check if it was pre-existing (manual conversion)
    if prim_filename in pre_existing_prim:
        print(f"Skipping {filename}, pre-existing manual conversion found.")
        return
        
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    converted = convert_py_to_prim(content, filename)
    
    with open(prim_path, 'w', encoding='utf-8') as f:
        f.write(converted)
    print(f"Converted {filename} to {prim_path}")

for filename in files_to_convert:
    process_file(filename)

# Handle remaining files
for filename in os.listdir(old_base_dir):
    if filename.endswith(".py") and filename not in files_to_convert:
        process_file(filename)

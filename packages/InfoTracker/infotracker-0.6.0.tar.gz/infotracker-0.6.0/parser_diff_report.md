# Parser functions diff report

## Summary
- Functions in DEV: **112**
- Functions in NEW: **202**
- Common: **106** | Missing in NEW: **6** | Added in NEW: **96**

## Missing in NEW (present in DEV)
- `SqlParser._apply_view_header_names` — _apply_view_header_names(self, create_exp, select_exp, obj)  *(at dev_parser.py:792)*
- `SqlParser._clean_output_name` — _clean_output_name(self, s)  *(at dev_parser.py:233)*
- `SqlParser._dequote` — _dequote(self, s)  *(at dev_parser.py:193)*
- `SqlParser._extract_column_type` — _extract_column_type(self, column_def)  *(at dev_parser.py:2810)*
- `SqlParser._has_not_null_constraint` — _has_not_null_constraint(self, column_def)  *(at dev_parser.py:2839)*
- `SqlParser._prescan_temp_tables_string` — _prescan_temp_tables_string(self, sql_content)  *(at dev_parser.py:5269)*

## Added in NEW (absent in DEV)
- `SqlParser._canonical_namespace` — _canonical_namespace(self, db)  *(at parser.py:157)*
- `_analyze_expression_lineage` — _analyze_expression_lineage(self, output_name, expr, context)  *(at select_lineage.py:442)*
- `_append_column_ref` — _append_column_ref(self, out_list, col_exp, alias_map)  *(at select_lineage.py:88)*
- `_apply_view_header_names` — _apply_view_header_names(self, create_exp, select_exp, obj)  *(at create_handlers.py:377)*
- `_build_alias_maps` — _build_alias_maps(self, select_exp)  *(at select_lineage.py:27)*
- `_canonical_namespace` — _canonical_namespace(self, db)  *(at names.py:162)*
- `_canonical_temp_name` — _canonical_temp_name(self, name)  *(at temp_utils.py:49)*
- `_choose_db` — _choose_db(self, counter)  *(at db_infer.py:62)*
- `_clean_proc_name` — _clean_proc_name(self, s)  *(at names.py:20)*
- `_collect_inputs_for_expr` — _collect_inputs_for_expr(self, expr, alias_map, derived_cols)  *(at select_lineage.py:124)*
- `_cut_to_first_statement` — _cut_to_first_statement(self, sql)  *(at preprocess.py:139)*
- `_expand_dependency_to_base_tables` — _expand_dependency_to_base_tables(self, dep_name, context_stmt)  *(at deps.py:57)*
- `_extract_basic_dependencies` — _extract_basic_dependencies(self, sql_content)  *(at deps.py:86)*
- `_extract_basic_lineage_from_select` — _extract_basic_lineage_from_select(self, select_sql, output_columns, object_name)  *(at string_fallbacks.py:335)*
- `_extract_basic_select_columns` — _extract_basic_select_columns(self, select_sql)  *(at string_fallbacks.py:245)*
- `_extract_column_alias` — _extract_column_alias(self, select_expr)  *(at select_lineage.py:227)*
- `_extract_column_lineage` — _extract_column_lineage(self, stmt, view_name)  *(at select_lineage.py:382)*
- `_extract_column_references` — _extract_column_references(self, select_expr, select_stmt)  *(at select_lineage.py:249)*
- `_extract_column_type` — _extract_column_type(self, column_def)  *(at create_handlers.py:118)*
- `_extract_database_from_use_statement` — _extract_database_from_use_statement(self, content)  *(at preprocess.py:120)*
- `_extract_dbt_model_name` — _extract_dbt_model_name(self, sql_text)  *(at preprocess.py:102)*
- `_extract_dependencies` — _extract_dependencies(self, stmt)  *(at deps.py:10)*
- `_extract_first_create_statement` — _extract_first_create_statement(self, sql_content, statement_type)  *(at string_fallbacks.py:113)*
- `_extract_function_name` — _extract_function_name(self, sql_content)  *(at functions.py:112)*
- `_extract_insert_select_lineage_string` — _extract_insert_select_lineage_string(self, sql_content, object_name)  *(at string_fallbacks.py:48)*
- `_extract_materialized_output_from_procedure_string` — _extract_materialized_output_from_procedure_string(self, sql_content)  *(at string_fallbacks.py:71)*
- `_extract_merge_lineage_string` — _extract_merge_lineage_string(self, sql_content, procedure_name)  *(at string_fallbacks.py:647)*
- `_extract_mstvf_lineage` — _extract_mstvf_lineage(self, statement, function_name, output_columns)  *(at create_handlers.py:584)*
- `_extract_output_into_lineage_string` — _extract_output_into_lineage_string(self, sql_content)  *(at string_fallbacks.py:459)*
- `_extract_procedure_lineage` — _extract_procedure_lineage(self, statement, procedure_name)  *(at create_handlers.py:534)*
- `_extract_procedure_lineage_string` — _extract_procedure_lineage_string(self, sql_content, procedure_name)  *(at string_fallbacks.py:592)*
- `_extract_procedure_name` — _extract_procedure_name(self, sql_content)  *(at procedures.py:206)*
- `_extract_procedure_outputs` — _extract_procedure_outputs(self, statement)  *(at create_handlers.py:406)*
- `_extract_select_from_return` — _extract_select_from_return(self, statement)  *(at create_handlers.py:547)*
- `_extract_select_from_return_string` — _extract_select_from_return_string(self, sql_content)  *(at functions.py:78)*
- `_extract_table_aliases_from_select` — _extract_table_aliases_from_select(self, select_sql)  *(at string_fallbacks.py:281)*
- `_extract_table_variable_schema` — _extract_table_variable_schema(self, statement)  *(at create_handlers.py:562)*
- `_extract_table_variable_schema_string` — _extract_table_variable_schema_string(self, sql_content)  *(at string_fallbacks.py:221)*
- `_extract_temp_name` — _extract_temp_name(self, raw_name)  *(at temp_utils.py:68)*
- `_extract_tvf_lineage` — _extract_tvf_lineage(self, statement, function_name)  *(at create_handlers.py:496)*
- `_extract_tvf_lineage_string` — _extract_tvf_lineage_string(self, sql_text, function_name)  *(at string_fallbacks.py:625)*
- `_extract_update_from_lineage_string` — _extract_update_from_lineage_string(self, sql_content)  *(at string_fallbacks.py:364)*
- `_extract_view_header_cols` — _extract_view_header_cols(self, create_exp)  *(at select_lineage.py:194)*
- `_find_last_select_in_procedure` — _find_last_select_in_procedure(self, statement)  *(at create_handlers.py:630)*
- `_find_last_select_string` — _find_last_select_string(self, sql_content, dialect)  *(at string_fallbacks.py:10)*
- `_find_last_select_string_fallback` — _find_last_select_string_fallback(self, sql_content)  *(at string_fallbacks.py:25)*
- `_get_full_table_name` — _get_full_table_name(self, table_name)  *(at names.py:119)*
- `_get_namespace_for_table` — _get_namespace_for_table(self, table_name)  *(at names.py:147)*
- `_get_schema` — _get_schema(self, db, sch, tbl)  *(at select_lineage.py:138)*
- `_get_table_name` — _get_table_name(self, table_expr, hint)  *(at names.py:93)*
- `_handle_star_expansion` — _handle_star_expansion(self, select_stmt, view_name)  *(at select_lineage.py:290)*
- `_handle_union_lineage` — _handle_union_lineage(self, stmt, view_name)  *(at select_lineage.py:351)*
- `_has_not_null_constraint` — _has_not_null_constraint(self, column_def)  *(at create_handlers.py:141)*
- `_has_star_expansion` — _has_star_expansion(self, select_stmt)  *(at select_lineage.py:276)*
- `_has_union` — _has_union(self, stmt)  *(at select_lineage.py:286)*
- `_infer_database_for_object` — _infer_database_for_object(self, statement, sql_text)  *(at db_infer.py:71)*
- `_infer_db_candidates_from_ast` — _infer_db_candidates_from_ast(self, node)  *(at db_infer.py:16)*
- `_infer_db_candidates_from_sql` — _infer_db_candidates_from_sql(self, sql_text)  *(at db_infer.py:38)*
- `_infer_type` — _infer_type(self, expr, alias_map)  *(at select_lineage.py:159)*
- `_is_cte_reference` — _is_cte_reference(self, dep_name)  *(at deps.py:81)*
- `_is_insert_exec` — _is_insert_exec(self, statement)  *(at dml.py:13)*
- `_is_select_into` — _is_select_into(self, statement)  *(at dml.py:9)*
- `_is_string_function` — _is_string_function(self, expr)  *(at select_lineage.py:270)*
- `_is_table_valued_function` — _is_table_valued_function(self, statement)  *(at create_handlers.py:25)*
- `_is_table_valued_function_string` — _is_table_valued_function_string(self, sql_content)  *(at functions.py:106)*
- `_normalize_table_ident` — _normalize_table_ident(self, s)  *(at names.py:28)*
- `_normalize_table_name_for_output` — _normalize_table_name_for_output(self, table_name)  *(at names.py:136)*
- `_normalize_tsql` — _normalize_tsql(self, text)  *(at preprocess.py:79)*
- `_ns_and_name` — _ns_and_name(self, table_name, obj_type_hint)  *(at names.py:45)*
- `_parse_column_expression` — _parse_column_expression(self, col_expr, table_aliases)  *(at string_fallbacks.py:297)*
- `_parse_create_function` — _parse_create_function(self, statement, object_hint)  *(at create_handlers.py:240)*
- `_parse_create_procedure` — _parse_create_procedure(self, statement, object_hint)  *(at create_handlers.py:281)*
- `_parse_create_statement` — _parse_create_statement(self, statement, object_hint)  *(at create_handlers.py:12)*
- `_parse_create_table` — _parse_create_table(self, statement, object_hint)  *(at create_handlers.py:34)*
- `_parse_create_table_string` — _parse_create_table_string(self, sql, object_hint)  *(at create_handlers.py:78)*
- `_parse_create_view` — _parse_create_view(self, statement, object_hint)  *(at create_handlers.py:155)*
- `_parse_function_string` — _parse_function_string(self, sql_content, object_hint)  *(at functions.py:11)*
- `_parse_insert_exec` — _parse_insert_exec(self, statement, object_hint)  *(at dml.py:100)*
- `_parse_insert_select` — _parse_insert_select(self, statement, object_hint)  *(at dml.py:179)*
- `_parse_procedure_string` — _parse_procedure_string(self, sql_content, object_hint)  *(at procedures.py:11)*
- `_parse_select_into` — _parse_select_into(self, statement, object_hint)  *(at dml.py:23)*
- `_preprocess_sql` — _preprocess_sql(self, sql)  *(at preprocess.py:153)*
- `_proc_acc_add` — _proc_acc_add(self, target_fqn, col_lineage)  *(at temp_utils.py:12)*
- `_proc_acc_finalize` — _proc_acc_finalize(self, target_fqn)  *(at temp_utils.py:23)*
- `_proc_acc_init` — _proc_acc_init(self, target_fqn)  *(at temp_utils.py:8)*
- `_process_ctes` — _process_ctes(self, select_stmt)  *(at select_lineage.py:632)*
- `_qualify_table` — _qualify_table(self, tbl)  *(at names.py:86)*
- `_resolve_table_from_alias` — _resolve_table_from_alias(self, alias, context)  *(at select_lineage.py:612)*
- `_rewrite_ast` — _rewrite_ast(self, root)  *(at preprocess.py:187)*
- `_short_desc` — _short_desc(self, expr)  *(at select_lineage.py:190)*
- `_split_fqn` — _split_fqn(self, fqn)  *(at names.py:37)*
- `_strip_sql_comments` — _strip_sql_comments(self, sql)  *(at db_infer.py:8)*
- `_temp_current` — _temp_current(self, name)  *(at temp_utils.py:44)*
- `_temp_next` — _temp_next(self, name)  *(at temp_utils.py:38)*
- `_try_insert_exec_fallback` — _try_insert_exec_fallback(self, sql_content, object_hint)  *(at string_fallbacks.py:134)*
- `_type_of_column` — _type_of_column(self, col_exp, alias_map)  *(at select_lineage.py:146)*

## Rename/move suggestions (for missing in NEW)
- `SqlParser._prescan_temp_tables_string` → candidates: `_extract_output_into_lineage_string` (sim=0.93), `_extract_merge_lineage_string` (sim=0.93), `_parse_insert_exec` (sim=0.91)
- `SqlParser._dequote` → candidates: `_normalize_table_ident` (sim=0.91), `_has_star_expansion` (sim=0.91), `_get_namespace_for_table` (sim=0.91)
- `SqlParser._has_not_null_constraint` → candidates: `_has_not_null_constraint` (sim=0.95), `_infer_type` (sim=0.92), `_apply_view_header_names` (sim=0.92)
- `SqlParser._clean_output_name` → candidates: `_extract_view_header_cols` (sim=0.93), `_extract_table_variable_schema_string` (sim=0.93), `_extract_column_type` (sim=0.93)
- `SqlParser._apply_view_header_names` → candidates: `_apply_view_header_names` (sim=0.97), `_process_ctes` (sim=0.95), `_append_column_ref` (sim=0.94)
- `SqlParser._extract_column_type` → candidates: `_extract_column_type` (sim=0.94), `_extract_basic_select_columns` (sim=0.93), `_process_ctes` (sim=0.92)

## Changed bodies / signatures (common functions)

### SqlParser._analyze_expression_lineage
- DEV: `_analyze_expression_lineage(self, output_name, expr, context)` *(at dev_parser.py:3095)*
- NEW: `_analyze_expression_lineage(self, output_name, expr, context)` *(at parser.py:745)*
- **Body changed** (AST-hash)
- Calls added: ['_analyze_expression_lineage']
- Calls removed: ['ColumnLineage', 'ColumnReference', '_is_string_function', '_ns_and_name', '_resolve_table_from_alias', 'add', 'append', 'endswith', 'find_all', 'hasattr', 'isinstance', 'join', 'len', 'replace', 'set', 'split', 'startswith', 'str', 'type', 'upper']

```diff
--- DEV/dev_parser.py:3095
+++ NEW/parser.py:745
@@ -1,297 +1,3 @@
 def _analyze_expression_lineage(self, output_name: str, expr: exp.Expression, context: exp.Select) -> ColumnLineage:
-        """Analyze an expression to determine its lineage."""
-        input_fields = []
-        transformation_type = TransformationType.IDENTITY
-        description = ""
-        
-        if isinstance(expr, exp.Column):
-            # Simple column reference
-            table_alias = str(expr.table) if expr.table else None
-            column_name = str(expr.this)
-            
-            # Resolve table name from alias
-            table_name = self._resolve_table_from_alias(table_alias, context)
-            # Skip noise identifiers (variables, dynamic tokens, bracket-only)
-            if table_name and (table_name.startswith('@') or ('+' in table_name) or (table_name.startswith('[') and table_name.endswith(']') and '.' not in table_name)):
-                return ColumnLineage(
-                    output_column=output_name,
-                    input_fields=[],
-                    transformation_type=TransformationType.EXPRESSION,
-                    transformation_description=f"Expression: {str(expr)}"
-                )
-            
-            ns, nm = self._ns_and_name(table_name)
-            input_fields.append(ColumnReference(
-                namespace=ns,
-                table_name=nm,
-                column_name=column_name
-            ))
-            
-            # Logic for RENAME vs IDENTITY based on expected patterns
-            table_simple = table_name.split('.')[-1] if '.' in table_name else table_name
-            
-            # Use RENAME for semantic renaming (like OrderItemID -> SalesID)
-            # Use IDENTITY for table/context changes (like ExtendedPrice -> Revenue)
-            semantic_renames = {
-                ('OrderItemID', 'SalesID'): True,
-                # Add other semantic renames as needed
-            }
-            
-            if (column_name, output_name) in semantic_renames:
-                transformation_type = TransformationType.RENAME
-                description = f"{column_name} AS {output_name}"
-            else:
-                # Default to IDENTITY with descriptive text
-                description = f"{output_name} from {table_simple}.{column_name}"
-            
-        elif isinstance(expr, exp.Cast):
-            # CAST expression - check if it contains arithmetic inside
-            transformation_type = TransformationType.CAST
-            inner_expr = expr.this
-            target_type = str(expr.to).upper()
-            
-            # Check if the inner expression is arithmetic
-            if isinstance(inner_expr, (exp.Mul, exp.Add, exp.Sub, exp.Div)):
-                transformation_type = TransformationType.ARITHMETIC
-                
-                # Extract columns from the arithmetic expression
-                for column_ref in inner_expr.find_all(exp.Column):
-                    table_alias = str(column_ref.table) if column_ref.table else None
-                    column_name = str(column_ref.this)
-                    table_name = self._resolve_table_from_alias(table_alias, context)
-                    
-                    ns, nm = self._ns_and_name(table_name)
-                    input_fields.append(ColumnReference(
-                        namespace=ns,
-                        table_name=nm,
-                        column_name=column_name
-                    ))
-                
-                # Create simplified description for arithmetic operations
-                expr_str = str(inner_expr)
-                if '*' in expr_str:
-                    operands = [str(col.this) for col in inner_expr.find_all(exp.Column)]
-                    if len(operands) >= 2:
-                        description = f"{operands[0]} * {operands[1]}"
-                    else:
-                        description = expr_str
-                else:
-                    description = expr_str
-            elif isinstance(inner_expr, exp.Column):
-                # Simple column cast
-                table_alias = str(inner_expr.table) if inner_expr.table else None
-                column_name = str(inner_expr.this)
-                table_name = self._resolve_table_from_alias(table_alias, context)
-                
-                ns, nm = self._ns_and_name(table_name)
-                input_fields.append(ColumnReference(
-                    namespace=ns,
-                    table_name=nm,
-                    column_name=column_name
-                ))
-                description = f"CAST({column_name} AS {target_type})"
-            
-        elif isinstance(expr, exp.Case):
-            # CASE expression
-            transformation_type = TransformationType.CASE
-            
-            # Extract columns referenced in CASE conditions and values
-            for column_ref in expr.find_all(exp.Column):
-                table_alias = str(column_ref.table) if column_ref.table else None
-                column_name = str(column_ref.this)
-                table_name = self._resolve_table_from_alias(table_alias, context)
-                
-                ns, nm = self._ns_and_name(table_name)
-                input_fields.append(ColumnReference(
-                    namespace=ns,
-                    table_name=nm,
-                    column_name=column_name
-                ))
-            
-            # Create a more detailed description for CASE expressions
-            description = str(expr).replace('\n', ' ').replace('  ', ' ')
-            
-        elif isinstance(expr, (exp.Sum, exp.Count, exp.Avg, exp.Min, exp.Max)):
-            # Aggregation functions
-            transformation_type = TransformationType.AGGREGATION
-            func_name = type(expr).__name__.upper()
-            
-            # Extract columns from the aggregation function
-            for column_ref in expr.find_all(exp.Column):
-                table_alias = str(column_ref.table) if column_ref.table else None
-                column_name = str(column_ref.this)
-                table_name = self._resolve_table_from_alias(table_alias, context)
-                
-                ns, nm = self._ns_and_name(table_name)
-                input_fields.append(ColumnReference(
-                    namespace=ns,
-                    table_name=nm,
-                    column_name=column_name
-                ))
-            
-            description = f"{func_name}({str(expr.this) if hasattr(expr, 'this') else '*'})"
-            
-        elif isinstance(expr, exp.Window):
-            # Window functions 
-            transformation_type = TransformationType.WINDOW
-            
-            # Extract columns from the window function arguments
-            # Window function structure: function() OVER (PARTITION BY ... ORDER BY ...)
-            inner_function = expr.this  # The function being windowed (ROW_NUMBER, SUM, etc.)
-            
-            # Extract columns from function arguments
-            if hasattr(inner_function, 'find_all'):
-                for column_ref in inner_function.find_all(exp.Column):
-                    table_alias = str(column_ref.table) if column_ref.table else None
-                    column_name = str(column_ref.this)
-                    table_name = self._resolve_table_from_alias(table_alias, context)
-                    
-                    ns, nm = self._ns_and_name(table_name)
-                    input_fields.append(ColumnReference(
-                        namespace=ns,
-                        table_name=nm,
-                        column_name=column_name
-                    ))
-            
-            # Extract columns from PARTITION BY clause
-            if hasattr(expr, 'partition_by') and expr.partition_by:
-                for partition_col in expr.partition_by:
-                    for column_ref in partition_col.find_all(exp.Column):
-                        table_alias = str(column_ref.table) if column_ref.table else None
-                        column_name = str(column_ref.this)
-                        table_name = self._resolve_table_from_alias(table_alias, context)
-                        
-                        ns, nm = self._ns_and_name(table_name)
-                        input_fields.append(ColumnReference(
-                            namespace=ns,
-                            table_name=nm,
-                            column_name=column_name
-                        ))
-            
-            # Extract columns from ORDER BY clause
-            if hasattr(expr, 'order') and expr.order:
-                for order_col in expr.order.expressions:
-                    for column_ref in order_col.find_all(exp.Column):
-                        table_alias = str(column_ref.table) if column_ref.table else None
-                        column_name = str(column_ref.this)
-                        table_name = self._resolve_table_from_alias(table_alias, context)
-                        
-                        ns, nm = self._ns_and_name(table_name)
-                        input_fields.append(ColumnReference(
-                            namespace=ns,
-                            table_name=nm,
-                            column_name=column_name
-                        ))
-            
-            # Create description
-            func_name = str(inner_function) if inner_function else "UNKNOWN"
-            partition_cols = []
-            order_cols = []
-            
-            if hasattr(expr, 'partition_by') and expr.partition_by:
-                partition_cols = [str(col) for col in expr.partition_by]
-            if hasattr(expr, 'order') and expr.order:
-                order_cols = [str(col) for col in expr.order.expressions]
-            
-            description = f"{func_name} OVER ("
-            if partition_cols:
-                description += f"PARTITION BY {', '.join(partition_cols)}"
-            if order_cols:
-                if partition_cols:
-                    description += " "
-                description += f"ORDER BY {', '.join(order_cols)}"
-            description += ")"
-            
-        elif isinstance(expr, (exp.Mul, exp.Add, exp.Sub, exp.Div)):
-            # Arithmetic operations
-            transformation_type = TransformationType.ARITHMETIC
-            
-            # Extract columns from the arithmetic expression (deduplicate)
-            seen_columns = set()
-            for column_ref in expr.find_all(exp.Column):
-                table_alias = str(column_ref.table) if column_ref.table else None
-                column_name = str(column_ref.this)
-                table_name = self._resolve_table_from_alias(table_alias, context)
-                
-                column_key = (table_name, column_name)
-                if column_key not in seen_columns:
-                    seen_columns.add(column_key)
-                    ns, nm = self._ns_and_name(table_name)
-                    input_fields.append(ColumnReference(
-                        namespace=ns,
-                        table_name=nm,
-                        column_name=column_name
-                    ))
-            
-            # Create simplified description for known patterns
-            expr_str = str(expr)
-            if '*' in expr_str:
-                # Extract operands for multiplication
-                operands = [str(col.this) for col in expr.find_all(exp.Column)]
-                if len(operands) >= 2:
-                    description = f"{operands[0]} * {operands[1]}"
-                else:
-                    description = expr_str
-            else:
-                description = expr_str
-                
-        elif self._is_string_function(expr):
-            # String parsing operations
-            transformation_type = TransformationType.STRING_PARSE
-            
-            # Extract columns from the string function (deduplicate by table and column name)
-            seen_columns = set()
-            for column_ref in expr.find_all(exp.Column):
-                table_alias = str(column_ref.table) if column_ref.table else None
-                column_name = str(column_ref.this)
-                table_name = self._resolve_table_from_alias(table_alias, context)
-                
-                # Deduplicate based on table and column name
-                column_key = (table_name, column_name)
-                if column_key not in seen_columns:
-                    seen_columns.add(column_key)
-                    ns, nm = self._ns_and_name(table_name)
-                    input_fields.append(ColumnReference(
-                        namespace=ns,
-                        table_name=nm,
-                        column_name=column_name
-                    ))
-            
-            # Create a cleaner description - try to match expected format
-            expr_str = str(expr)
-            # Try to clean up SQLGlot's verbose output
-            if 'RIGHT' in expr_str.upper() and 'LEN' in expr_str.upper() and 'CHARINDEX' in expr_str.upper():
-                # Extract the column name for the expected format
-                columns = [str(col.this) for col in expr.find_all(exp.Column)]
-                if columns:
-                    col_name = columns[0]
-                    description = f"RIGHT({col_name}, LEN({col_name}) - CHARINDEX('@', {col_name}))"
-                else:
-                    description = expr_str
-            else:
-                description = expr_str
-            
-        else:
-            # Other expressions - extract all column references
-            transformation_type = TransformationType.EXPRESSION
-            
-            for column_ref in expr.find_all(exp.Column):
-                table_alias = str(column_ref.table) if column_ref.table else None
-                column_name = str(column_ref.this)
-                table_name = self._resolve_table_from_alias(table_alias, context)
-                
-                ns, nm = self._ns_and_name(table_name)
-                input_fields.append(ColumnReference(
-                    namespace=ns,
-                    table_name=nm,
-                    column_name=column_name
-                ))
-            
-            description = f"Expression: {str(expr)}"
-        
-        return ColumnLineage(
-            output_column=output_name,
-            input_fields=input_fields,
-            transformation_type=transformation_type,
-            transformation_description=description
-        )
+        from .parser_modules import select_lineage as _sl
+        return _sl._analyze_expression_lineage(self, output_name, expr, context)
```

### SqlParser._append_column_ref
- DEV: `_append_column_ref(self, out_list, col_exp, alias_map)` *(at dev_parser.py:647)*
- NEW: `_append_column_ref(self, out_list, col_exp, alias_map)` *(at parser.py:192)*
- **Body changed** (AST-hash)
- Calls added: ['_append_column_ref']
- Calls removed: ['ColumnReference', '_canonical_temp_name', '_split_fqn', '_temp_current', 'append', 'extend', 'get', 'lower', 'split', 'startswith', 'str', 'upper']

```diff
--- DEV/dev_parser.py:647
+++ NEW/parser.py:192
@@ -1,36 +1,3 @@
 def _append_column_ref(self, out_list, col_exp: exp.Column, alias_map: dict):
-        """Append a column reference to the output list after resolving aliases."""
-        qual = (col_exp.table or "").lower()
-        table_fqn = alias_map.get(qual)
-        if not table_fqn:
-            return
-        db, sch, tbl = self._split_fqn(table_fqn)
-        # Expand temp table column refs to their base lineage if known
-        try:
-            # temp detection: any segment with '#'
-            temp_seg = None
-            for seg in (table_fqn or '').split('.'):
-                if str(seg).startswith('#'):
-                    temp_seg = seg
-                    break
-            if temp_seg:
-                # Always include the temp itself as an input (canonical name)
-                temp_canon = self._canonical_temp_name(temp_seg)
-                ns_temp = f"mssql://localhost/{(self._ctx_db or db or 'InfoTrackerDW').upper()}"
-                out_list.append(ColumnReference(namespace=ns_temp, table_name=temp_canon, column_name=col_exp.name))
-                # And then, if we know its base lineage, include it as well (inline)
-                ver = self._temp_current(temp_seg)
-                colname = col_exp.name
-                if ver and ver in self.temp_lineage and colname in self.temp_lineage[ver]:
-                    out_list.extend(self.temp_lineage[ver][colname])
-                    return
-                if temp_seg in self.temp_lineage and colname in self.temp_lineage[temp_seg]:
-                    out_list.extend(self.temp_lineage[temp_seg][colname])
-                    return
-        except Exception:
-            pass
-        out_list.append(ColumnReference(
-            namespace=f"mssql://localhost/{(db or 'InfoTrackerDW').upper()}" if db else "mssql://localhost",
-            table_name=f"{sch}.{tbl}",  # <== tylko schema.table (non-temp)
-            column_name=col_exp.name
-        ))
+        from .parser_modules import select_lineage as _sl
+        return _sl._append_column_ref(self, out_list, col_exp, alias_map)
```

### SqlParser._build_alias_maps
- DEV: `_build_alias_maps(self, select_exp)` *(at dev_parser.py:582)*
- NEW: `_build_alias_maps(self, select_exp)` *(at parser.py:188)*
- **Body changed** (AST-hash)
- Calls added: ['_build_alias_maps']
- Calls removed: ['_canonical_temp_name', '_qualify_table', 'append', 'find_all', 'get', 'getattr', 'hasattr', 'isinstance', 'len', 'list', 'lower', 'set', 'sorted', 'split', 'startswith', 'str']

```diff
--- DEV/dev_parser.py:582
+++ NEW/parser.py:188
@@ -1,64 +1,3 @@
 def _build_alias_maps(self, select_exp: exp.Select):
-        """Build maps for table aliases and derived table columns."""
-        alias_map = {}       # alias_lower -> DB.sch.tbl
-        derived_cols = {}    # (alias_lower, out_col_lower) -> list[exp.Column] (base cols of subquery projection)
-
-        # Plain tables
-        base_fqns = []
-        for t in select_exp.find_all(exp.Table):
-            a = getattr(t, "alias", None) or t.args.get("alias")
-            alias = None
-            if a:
-                # Handle both string aliases and alias objects
-                if hasattr(a, "name"):
-                    alias = a.name.lower()
-                else:
-                    alias = str(a).lower()
-            fqn = self._qualify_table(t)
-            # If this table corresponds to a known temp by simple name, canonicalize mapping to the temp
-            try:
-                parts_tmp = (fqn or '').split('.')
-                simple = parts_tmp[-1] if parts_tmp else None
-                if simple and not str(simple).startswith('#') and (f"#{simple}" in self.temp_registry):
-                    fqn = self._canonical_temp_name(f"#{simple}")
-            except Exception:
-                pass
-            if alias: 
-                alias_map[alias] = fqn
-            alias_map[t.name.lower()] = fqn
-            base_fqns.append(fqn)
-
-        # Derived tables (subqueries with alias)
-        for sq in select_exp.find_all(exp.Subquery):
-            a = getattr(sq, "alias", None) or sq.args.get("alias")
-            if not a: 
-                continue
-            # Handle both string aliases and alias objects
-            if hasattr(a, "name"):
-                alias = a.name.lower()
-            else:
-                alias = str(a).lower()
-            inner = sq.this if isinstance(sq.this, exp.Select) else None
-            if not inner:
-                continue
-            idx = 0
-            for proj in (inner.expressions or []):
-                if isinstance(proj, exp.Alias):
-                    out_name = (proj.alias or proj.alias_or_name)
-                    target = proj.this
-                else:
-                    out_name = f"col_{idx+1}"
-                    target = proj
-                key = (alias, (out_name or "").lower())
-                derived_cols[key] = list(target.find_all(exp.Column))
-                idx += 1
-
-        # If there is exactly one base table in FROM, allow resolving unqualified columns to it
-        try:
-            uniq = sorted(set(base_fqns))
-            if len(uniq) == 1 and '' not in alias_map:
-                alias_map[''] = uniq[0]
-        except Exception:
-            pass
-
-        return alias_map, derived_cols
+        from .parser_modules import select_lineage as _sl
+        return _sl._build_alias_maps(self, select_exp)
```

### SqlParser._canonical_temp_name
- DEV: `_canonical_temp_name(self, temp_name)` *(at dev_parser.py:256)*
- NEW: `_canonical_temp_name(self, name)` *(at parser.py:76)*
- **Signature changed**
- **Body changed** (AST-hash)
- Calls added: ['_canonical_temp_name']
- Calls removed: ['_extract_temp_name', 'rsplit', 'split', 'startswith']

```diff
--- DEV/dev_parser.py:256
+++ NEW/parser.py:76
@@ -1,22 +1,3 @@
-def _canonical_temp_name(self, temp_name: str) -> str:
-        """Build canonical name for a temp table: DB.schema.object.#temp.
-
-        temp_name: '#tmp' or 'tempdb..#tmp' or just '#tmp@v'
-        Uses current object context if available; otherwise falls back to
-        default schema + file stem.
-        """
-        # Extract simple '#name' using _extract_temp_name to clean it
-        raw_t = (temp_name or "").split('.')[-1]
-        t = self._extract_temp_name(raw_t) if '#' in raw_t else raw_t
-        if not t.startswith('#'):
-            t = f"#{t}"
-        db = self._ctx_db or self.current_database or self.default_database or 'InfoTrackerDW'
-        obj = self._ctx_obj
-        if not obj:
-            # Fallback: derive from file name
-            try:
-                stem = (self._current_file or '').split('/')[-1].rsplit('.', 1)[0]
-            except Exception:
-                stem = (self._current_file or 'unknown').split('/')[-1]
-            obj = f"{self.default_schema or 'dbo'}.{stem or 'unknown'}"
-        return f"{db}.{obj}.{t}"
+def _canonical_temp_name(self, name: str) -> str:
+        from .parser_modules import temp_utils as _tu
+        return _tu._canonical_temp_name(self, name)
```

### SqlParser._choose_db
- DEV: `_choose_db(self, counter)` *(at dev_parser.py:530)*
- NEW: `_choose_db(self, counter)` *(at parser.py:174)*
- **Body changed** (AST-hash)
- Calls added: ['_choose_db']
- Calls removed: ['len', 'most_common']

```diff
--- DEV/dev_parser.py:530
+++ NEW/parser.py:174
@@ -1,7 +1,3 @@
 def _choose_db(self, counter) -> Optional[str]:
-        if not counter:
-            return None
-        mc = counter.most_common()
-        if len(mc) == 1 or (len(mc) > 1 and mc[0][1] > mc[1][1]):
-            return mc[0][0]
-        return None
+        from .parser_modules import db_infer as _db
+        return _db._choose_db(self, counter)
```

### SqlParser._clean_proc_name
- DEV: `_clean_proc_name(self, s)` *(at dev_parser.py:189)*
- NEW: `_clean_proc_name(self, s)` *(at parser.py:84)*
- **Body changed** (AST-hash)
- Calls added: ['_clean_proc_name']
- Calls removed: ['rstrip', 'split', 'strip']

```diff
--- DEV/dev_parser.py:189
+++ NEW/parser.py:84
@@ -1,3 +1,4 @@
 def _clean_proc_name(self, s: str) -> str:
         """Clean procedure name by removing semicolons and parameters."""
-        return s.strip().rstrip(';').split('(')[0].strip()
+        from .parser_modules import names as _names
+        return _names._clean_proc_name(self, s)
```

### SqlParser._collect_inputs_for_expr
- DEV: `_collect_inputs_for_expr(self, expr, alias_map, derived_cols)` *(at dev_parser.py:684)*
- NEW: `_collect_inputs_for_expr(self, expr, alias_map, derived_cols)` *(at parser.py:196)*
- **Body changed** (AST-hash)
- Calls added: ['_collect_inputs_for_expr']
- Calls removed: ['_append_column_ref', 'find_all', 'get', 'lower']

```diff
--- DEV/dev_parser.py:684
+++ NEW/parser.py:196
@@ -1,15 +1,3 @@
 def _collect_inputs_for_expr(self, expr: exp.Expression, alias_map: dict, derived_cols: dict):
-        """Collect input column references for an expression, resolving derived table aliases."""
-        inputs = []
-        for col in expr.find_all(exp.Column):
-            qual = (col.table or "").lower()
-            key = (qual, col.name.lower())
-            base_cols = derived_cols.get(key)
-            if base_cols:
-                # This column comes from a derived table - use its base columns
-                for b in base_cols:
-                    self._append_column_ref(inputs, b, alias_map)
-                continue
-            # Regular table column
-            self._append_column_ref(inputs, col, alias_map)
-        return inputs
+        from .parser_modules import select_lineage as _sl
+        return _sl._collect_inputs_for_expr(self, expr, alias_map, derived_cols)
```

### SqlParser._cut_to_first_statement
- DEV: `_cut_to_first_statement(self, sql)` *(at dev_parser.py:944)*
- NEW: `_cut_to_first_statement(self, sql)` *(at parser.py:252)*
- **Body changed** (AST-hash)
- Calls added: ['_cut_to_first_statement']
- Calls removed: ['compile', 'search', 'start']
- Regex removed: ['(?:CREATE\\s+(?:OR\\s+ALTER\\s+)?(?:VIEW|TABLE|FUNCTION|PROCEDURE)\\b|ALTER\\s+(?:VIEW|TABLE|FUNCTION|PROCEDURE)\\b|SELECT\\b.*?\\bINTO\\b|INSERT\\s+INTO\\b.*?\\bEXEC\\b)']

```diff
--- DEV/dev_parser.py:944
+++ NEW/parser.py:252
@@ -1,18 +1,7 @@
 def _cut_to_first_statement(self, sql: str) -> str:
         """
         Cut SQL content to start from the first significant statement.
         Looks for: CREATE [OR ALTER] VIEW|TABLE|FUNCTION|PROCEDURE, ALTER, SELECT...INTO, INSERT...EXEC
         """
-        
-        
-        pattern = re.compile(
-            r'(?:'
-            r'CREATE\s+(?:OR\s+ALTER\s+)?(?:VIEW|TABLE|FUNCTION|PROCEDURE)\b'
-            r'|ALTER\s+(?:VIEW|TABLE|FUNCTION|PROCEDURE)\b'
-            r'|SELECT\b.*?\bINTO\b'                # SELECT ... INTO (może być w wielu liniach)
-            r'|INSERT\s+INTO\b.*?\bEXEC\b'
-            r')',
-            re.IGNORECASE | re.DOTALL
-        )
-        m = pattern.search(sql)
-        return sql[m.start():] if m else sql
+        from .parser_modules import preprocess as _pp
+        return _pp._cut_to_first_statement(self, sql)
```

### SqlParser._expand_dependency_to_base_tables
- DEV: `_expand_dependency_to_base_tables(self, dep_name, context_stmt)` *(at dev_parser.py:5399)*
- NEW: `_expand_dependency_to_base_tables(self, dep_name, context_stmt)` *(at parser.py:948)*
- **Body changed** (AST-hash)
- Calls removed: ['_extract_dependencies', 'add', 'get', 'hasattr', 'isinstance', 'set', 'split', 'str', 'update']

```diff
--- DEV/dev_parser.py:5399
+++ NEW/parser.py:948
@@ -1,29 +1,3 @@
 def _expand_dependency_to_base_tables(self, dep_name: str, context_stmt: exp.Expression) -> Set[str]:
-        """Expand dependency to base tables, resolving CTEs and temp tables."""
-        expanded = set()
-        
-        # Check if this is a CTE reference
-        simple_name = dep_name.split('.')[-1]
-        if simple_name in self.cte_registry:
-            # This is a CTE - find its definition and get base dependencies
-            if isinstance(context_stmt, exp.Select) and context_stmt.args.get('with'):
-                with_clause = context_stmt.args.get('with')
-                if hasattr(with_clause, 'expressions'):
-                    for cte in with_clause.expressions:
-                        if hasattr(cte, 'alias') and str(cte.alias) == simple_name:
-                            if isinstance(cte.this, exp.Select):
-                                cte_deps = self._extract_dependencies(cte.this)
-                                for cte_dep in cte_deps:
-                                    expanded.update(self._expand_dependency_to_base_tables(cte_dep, cte.this))
-                            break
-            return expanded
-        
-        # Check if this is a temp table reference
-        if simple_name in self.temp_registry:
-            # For temp tables, return the temp table name itself (it's a base table)
-            expanded.add(dep_name)
-            return expanded
-        
-        # It's a regular table - return as is
-        expanded.add(dep_name)
-        return expanded
+        from .parser_modules import deps as _deps
+        return _deps._expand_dependency_to_base_tables(self, dep_name, context_stmt)
```

### SqlParser._extract_basic_dependencies
- DEV: `_extract_basic_dependencies(self, sql_content)` *(at dev_parser.py:4955)*
- NEW: `_extract_basic_dependencies(self, sql_content)` *(at parser.py:913)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_basic_dependencies']
- Calls removed: ['_canonical_temp_name', '_get_full_table_name', '_normalize_table_ident', '_strip_expr_tail', 'add', 'endswith', 'findall', 'len', 'lower', 'sanitize_name', 'search', 'set', 'split', 'startswith', 'strip', 'sub', 'upper']
- Regex removed: ['--.*?(?=\\n|$)', '/\\*.*?\\*/', '\\w+\\s*\\(']

```diff
--- DEV/dev_parser.py:4955
+++ NEW/parser.py:913
@@ -1,158 +1,4 @@
 def _extract_basic_dependencies(self, sql_content: str) -> Set[str]:
-        """Basic extraction of table dependencies from SQL."""
-        dependencies = set()
-        
-        # Remove comments to avoid false matches
-        cleaned_sql = re.sub(r'--.*?(?=\n|$)', '', sql_content, flags=re.MULTILINE)
-        cleaned_sql = re.sub(r'/\*.*?\*/', '', cleaned_sql, flags=re.DOTALL)
-        
-        # Find FROM and JOIN clauses with better patterns
-        # Match schema.table.name or table patterns
-        from_pattern = r'FROM\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        join_pattern = r'JOIN\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        update_pattern = r'UPDATE\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        delete_from_pattern = r'DELETE\s+FROM\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        merge_into_pattern = r'MERGE\s+INTO\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-
-
-        sql_keywords = {
-            'select','from','join','on','where','group','having','order','into',
-            'update','delete','merge','as','and','or','not','case','when','then','else','set',
-            'distinct','top','with','nolock','commit','rollback','transaction','begin','try','catch','exists'
-        }
-        builtin_functions = {
-            'getdate','sysdatetime','xact_state','row_number','count','sum','min','max','avg',
-            'cast','convert','try_convert','coalesce','isnull','iif','len','substring','replace',
-            'upper','lower','ltrim','rtrim','trim','dateadd','datediff','format','hashbytes','md5'
-        }
-        sql_types = {
-            'varchar','nvarchar','char','nchar','text','ntext',
-            'int','bigint','smallint','tinyint','numeric','decimal','money','smallmoney','float','real',
-            'bit','binary','varbinary','image',
-            'datetime','datetime2','smalldatetime','date','time','datetimeoffset',
-            'uniqueidentifier','xml','cursor','table'
-        }
-
-        update_matches = re.findall(update_pattern, cleaned_sql, re.IGNORECASE)
-        delete_matches = re.findall(delete_from_pattern, cleaned_sql, re.IGNORECASE)
-        merge_matches  = re.findall(merge_into_pattern, cleaned_sql, re.IGNORECASE)
-        from_matches = re.findall(from_pattern, cleaned_sql, re.IGNORECASE)
-        join_matches = re.findall(join_pattern, cleaned_sql, re.IGNORECASE)
-        
-        # Find function calls - both in FROM clauses and standalone
-        # Pattern for function calls with parentheses
-        function_call_pattern = r'(?:FROM\s+|SELECT\s+.*?\s+FROM\s+|,\s*)?([^\s\(\),]+(?:\.[^\s\(\),]+)*)\s*\([^)]*\)'
-        exec_pattern = r'EXEC\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        
-        function_matches = re.findall(function_call_pattern, cleaned_sql, re.IGNORECASE)
-        exec_matches = re.findall(exec_pattern, cleaned_sql, re.IGNORECASE)
-        
-        # Find table references in SELECT statements (for multi-table queries)
-        # This captures tables in complex queries where they might not be in FROM/JOIN
-        select_table_pattern = r'SELECT\s+.*?\s+FROM\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        select_matches = re.findall(select_table_pattern, cleaned_sql, re.IGNORECASE | re.DOTALL)
-        
-        # Also exclude INSERT INTO and CREATE TABLE targets from dependencies
-        # These are outputs, not inputs
-        insert_pattern = r'INSERT\s+INTO\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        create_pattern = r'CREATE\s+(?:OR\s+ALTER\s+)?(?:TABLE|VIEW|PROCEDURE|FUNCTION)\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        select_into_pattern = r'INTO\s+([^\s\(\),]+(?:\.[^\s\(\),]+)*)'
-        
-        insert_targets = set()
-        for match in re.findall(insert_pattern, cleaned_sql, re.IGNORECASE):
-            table_name = self._normalize_table_ident(_strip_expr_tail(match.strip()))
-            if not table_name.startswith('#'):
-                full_name = self._get_full_table_name(table_name)
-                parts = full_name.split('.')
-                if len(parts) >= 2:
-                    simplified = f"{parts[-2]}.{parts[-1]}"
-                    insert_targets.add(simplified)
-        
-        for match in re.findall(create_pattern, cleaned_sql, re.IGNORECASE):
-            table_name = self._normalize_table_ident(_strip_expr_tail(match.strip()))
-            if not table_name.startswith('#'):
-                full_name = self._get_full_table_name(table_name)
-                parts = full_name.split('.')
-                if len(parts) >= 2:
-                    simplified = f"{parts[-2]}.{parts[-1]}"
-                    insert_targets.add(simplified)
-        
-        for match in re.findall(select_into_pattern, cleaned_sql, re.IGNORECASE):
-            table_name = self._normalize_table_ident(_strip_expr_tail(match.strip()))
-            if not table_name.startswith('#'):
-                full_name = self._get_full_table_name(table_name)
-                parts = full_name.split('.')
-                if len(parts) >= 2:
-                    simplified = f"{parts[-2]}.{parts[-1]}"
-                    insert_targets.add(simplified)
-        
-        # Process tables, functions, and procedures (limit to core sources for performance)
-        all_matches = from_matches + join_matches + update_matches + delete_matches + merge_matches + exec_matches
-        for match in all_matches:
-            table_name = _strip_expr_tail(match.strip())
-
-            # jeżeli to wzorzec funkcji: "NAME(...)" – pomiń
-            if re.search(r'\w+\s*\(', table_name):
-                continue
-            # wymagaj nazwy w postaci schemat.katalog lub przynajmniej identyfikatora bez słów kluczowych
-            if table_name.lower() in builtin_functions:
-                continue
-
-            # Skip empty matches
-            if not table_name:
-                continue
-                
-            # Skip SQL keywords and built-in functions
-            
-            if table_name.lower() in sql_keywords or table_name.lower() in builtin_functions or table_name.lower() in sql_types:
-                continue
-                
-            # Remove table alias if present (e.g., "table AS t" -> "table")
-            if ' AS ' in table_name.upper():
-                table_name = table_name.split(' AS ')[0].strip()
-            elif ' ' in table_name and not '.' in table_name.split()[-1]:
-                # Just "table alias" format -> take first part
-                table_name = table_name.split()[0]
-            
-            # Clean brackets and normalize
-            table_name = self._normalize_table_ident(table_name)
-            
-            # Skip dynamic/variable/bracket-only tokens
-            if table_name.startswith('@'):
-                continue
-            if '+' in table_name:
-                continue
-            if table_name.startswith('[') and table_name.endswith(']') and '.' not in table_name:
-                continue
-
-            # Include temp tables; canonicalize them to DB.schema.object.#temp
-            if table_name.lower() not in sql_keywords:
-                if table_name.startswith('#') or table_name.lower().startswith('tempdb..#'):
-                    qualified_name = self._canonical_temp_name(table_name)
-                else:
-                    # Get full qualified name for consistent dependency tracking
-                    full_name = self._get_full_table_name(table_name)
-                    from .openlineage_utils import sanitize_name
-                    full_name = sanitize_name(full_name)
-
-                    # Always use fully qualified format: database.schema.table
-                    parts = full_name.split('.')
-                    if len(parts) >= 3:
-                        qualified_name = full_name  # Already has database.schema.table
-                    elif len(parts) == 2:
-                        # schema.table -> add database
-                        db_to_use = self.current_database or self.default_database or "InfoTrackerDW"
-                        qualified_name = f"{db_to_use}.{full_name}"
-                    else:
-                        # just table -> add default database and schema
-                        db_to_use = self.current_database or self.default_database or "InfoTrackerDW"
-                        qualified_name = f"{db_to_use}.dbo.{table_name}"
-
-                # Check if this is an output table (exclude from dependencies)
-                output_check_parts = qualified_name.split('.')
-                if len(output_check_parts) >= 2:
-                    simplified_for_check = f"{output_check_parts[-2]}.{output_check_parts[-1]}"
-                    if simplified_for_check not in insert_targets:
-                        dependencies.add(qualified_name)
-        
-        return dependencies
+        """Basic extraction of table dependencies from SQL (delegated)."""
+        from .parser_modules import deps as _deps
+        return _deps._extract_basic_dependencies(self, sql_content)
```

### SqlParser._extract_basic_lineage_from_select
- DEV: `_extract_basic_lineage_from_select(self, select_sql, output_columns, object_name)` *(at dev_parser.py:4854)*
- NEW: `_extract_basic_lineage_from_select(self, select_sql, output_columns, object_name)` *(at parser.py:898)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_basic_lineage_from_select']
- Calls removed: ['ColumnLineage', '_extract_table_aliases_from_select', '_log_debug', '_parse_column_expression', 'append', 'enumerate', 'group', 'search', 'split', 'strip', 'zip']
- Regex removed: ['SELECT\\s+(.*?)\\s+FROM']

```diff
--- DEV/dev_parser.py:4854
+++ NEW/parser.py:898
@@ -1,34 +1,4 @@
 def _extract_basic_lineage_from_select(self, select_sql: str, output_columns: List[ColumnSchema], object_name: str) -> List[ColumnLineage]:
         """Extract basic lineage information from SELECT statement using string parsing."""
-        lineage = []
-        
-        try:
-            # Extract table aliases from FROM and JOIN clauses
-            table_aliases = self._extract_table_aliases_from_select(select_sql)
-            
-            # Parse the SELECT list to match columns with their sources
-            select_match = re.search(r'SELECT\s+(.*?)\s+FROM', select_sql, re.IGNORECASE | re.DOTALL)
-            if not select_match:
-                return lineage
-                
-            select_list = select_match.group(1)
-            column_expressions = [col.strip() for col in select_list.split(',')]
-            
-            for i, (output_col, col_expr) in enumerate(zip(output_columns, column_expressions)):
-                # Try to find source table and column
-                source_table, source_column, transformation_type = self._parse_column_expression(col_expr, table_aliases)
-                
-                if source_table and source_column:
-                    lineage.append(ColumnLineage(
-                        column_name=output_col.name,
-                        table_name=object_name,
-                        source_column=source_column,
-                        source_table=source_table,
-                        transformation_type=transformation_type,
-                        transformation_description=f"Column derived from {source_table}.{source_column}"
-                    ))
-            
-        except Exception as e:
-            self._log_debug(f"Basic lineage extraction failed: {e}")
-            
-        return lineage
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_basic_lineage_from_select(self, select_sql, output_columns, object_name)
```

### SqlParser._extract_basic_select_columns
- DEV: `_extract_basic_select_columns(self, select_sql)` *(at dev_parser.py:4799)*
- NEW: `_extract_basic_select_columns(self, select_sql)` *(at parser.py:893)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_basic_select_columns']
- Calls removed: ['ColumnSchema', '_clean_output_name', 'any', 'append', 'enumerate', 'group', 'join', 'max', 'search', 'split', 'strip', 'sub', 'upper']
- Regex removed: ['--.*?$', '/\\*.*?\\*/', 'SELECT\\s+(.*?)\\s+FROM', '[^\\w]']

```diff
--- DEV/dev_parser.py:4799
+++ NEW/parser.py:893
@@ -1,54 +1,4 @@
 def _extract_basic_select_columns(self, select_sql: str) -> List[ColumnSchema]:
         """Basic extraction of column names from SELECT statement."""
-        output_columns = []
-        
-        # Extract the SELECT list (between SELECT and FROM)
-        match = re.search(r'SELECT\s+(.*?)\s+FROM', select_sql, re.IGNORECASE | re.DOTALL)
-        if match:
-            select_list = match.group(1)
-            # Remove comments to avoid leakage into names
-            try:
-                select_list = re.sub(r"/\*.*?\*/", "", select_list, flags=re.S)
-                select_list = re.sub(r"--.*?$", "", select_list, flags=re.M)
-            except Exception:
-                pass
-            # Depth-aware split on commas to avoid breaking inside functions/CASE
-            columns = []
-            buf = []
-            depth = 0
-            for ch in select_list:
-                if ch == '(':
-                    depth += 1
-                elif ch == ')':
-                    depth = max(0, depth - 1)
-                if ch == ',' and depth == 0:
-                    columns.append(''.join(buf).strip())
-                    buf = []
-                else:
-                    buf.append(ch)
-            if buf:
-                columns.append(''.join(buf).strip())
-            
-            for i, col in enumerate(columns):
-                # Handle aliases (column AS alias or column alias)
-                if ' AS ' in col.upper():
-                    col_name = col.split(' AS ')[-1].strip()
-                elif ' ' in col and not any(func in col.upper() for func in ['SUM', 'COUNT', 'MAX', 'MIN', 'AVG', 'CAST', 'CASE']):
-                    parts = col.strip().split()
-                    col_name = parts[-1]  # Last part is usually the alias
-                else:
-                    # Extract the base column name
-                    col_name = col.split('.')[-1] if '.' in col else col
-                    col_name = re.sub(r'[^\w]', '', col_name)  # Remove non-alphanumeric
-                # Clean: dequote, strip leading underscores, trim
-                col_name = self._clean_output_name(col_name) or f"col_{i+1}"
-                
-                if col_name:
-                    output_columns.append(ColumnSchema(
-                        name=col_name,
-                        data_type="varchar",  # Default type
-                        nullable=True,
-                        ordinal=i
-                    ))
-        
-        return output_columns
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_basic_select_columns(self, select_sql)
```

### SqlParser._extract_column_alias
- DEV: `_extract_column_alias(self, select_expr)` *(at dev_parser.py:5459)*
- NEW: `_extract_column_alias(self, select_expr)` *(at parser.py:960)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_column_alias']
- Calls removed: ['enumerate', 'hasattr', 'isinstance', 'len', 'split', 'str', 'strip', 'upper']

```diff
--- DEV/dev_parser.py:5459
+++ NEW/parser.py:960
@@ -1,21 +1,3 @@
 def _extract_column_alias(self, select_expr: exp.Expression) -> Optional[str]:
-        """Extract column alias from a SELECT expression."""
-        if hasattr(select_expr, 'alias') and select_expr.alias:
-            return str(select_expr.alias)
-        elif isinstance(select_expr, exp.Alias):
-            return str(select_expr.alias)
-        elif isinstance(select_expr, exp.Column):
-            return str(select_expr.this)
-        else:
-            # Try to extract from the expression itself
-            expr_str = str(select_expr)
-            if ' AS ' in expr_str.upper():
-                parts = expr_str.split()
-                as_idx = -1
-                for i, part in enumerate(parts):
-                    if part.upper() == 'AS':
-                        as_idx = i
-                        break
-                if as_idx >= 0 and as_idx + 1 < len(parts):
-                    return parts[as_idx + 1].strip("'\"")
-        return None
+        from .parser_modules import select_lineage as _sl
+        return _sl._extract_column_alias(self, select_expr)
```

### SqlParser._extract_column_lineage
- DEV: `_extract_column_lineage(self, stmt, view_name)` *(at dev_parser.py:2919)*
- NEW: `_extract_column_lineage(self, stmt, view_name)` *(at parser.py:741)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_column_lineage']
- Calls removed: ['ColumnLineage', 'ColumnReference', 'ColumnSchema', '_build_alias_maps', '_clean_output_name', '_collect_inputs_for_expr', '_dequote', '_extract_dependencies', '_handle_star_expansion', '_handle_union_lineage', '_has_star_expansion', '_has_union', '_infer_type', '_short_desc', '_split_fqn', 'append', 'find', 'get', 'getattr', 'hasattr', 'isinstance', 'len', 'list', 'set', 'sorted', 'split', 'startswith', 'str', 'upper']

```diff
--- DEV/dev_parser.py:2919
+++ NEW/parser.py:741
@@ -1,175 +1,3 @@
 def _extract_column_lineage(self, stmt: exp.Expression, view_name: str) -> tuple[List[ColumnLineage], List[ColumnSchema]]:
-        """Extract column lineage from SELECT or UNION statement using enhanced alias mapping."""
-        lineage = []
-        output_columns = []
-        
-        # Handle UNION at the top level
-        if isinstance(stmt, exp.Union):
-            return self._handle_union_lineage(stmt, view_name)
-        
-        # Must be a SELECT statement from here
-        if not isinstance(stmt, exp.Select):
-            return lineage, output_columns
-            
-        select_stmt = stmt
-        
-        # Build alias maps for proper resolution
-        alias_map, derived_cols = self._build_alias_maps(select_stmt)
-        
-        # Try to get projections with fallback
-        projections = list(getattr(select_stmt, 'expressions', None) or [])
-        if not projections:
-            return lineage, output_columns
-        
-        # Handle star expansion first
-        if self._has_star_expansion(select_stmt):
-            return self._handle_star_expansion(select_stmt, view_name)
-        
-        # Handle UNION operations within SELECT
-        if self._has_union(select_stmt):
-            return self._handle_union_lineage(select_stmt, view_name)
-        
-        # Enhanced column-by-column processing
-        ordinal = 0
-        for proj in projections:
-            # Skip variable assignments (@var = expression) in T-SQL
-            if isinstance(proj, exp.EQ):
-                # Check if left side is a variable
-                left = proj.this if hasattr(proj, 'this') else None
-                if left and str(left).startswith('@'):
-                    # This is a variable assignment, not a column projection
-                    continue
-            
-            # Decide output name using enhanced logic
-            if isinstance(proj, exp.Alias):
-                out_name = proj.alias or proj.alias_or_name
-                inner = proj.this
-            else:
-                # No explicit alias - try to get implicit name from SQLGlot
-                implicit_name = getattr(proj, 'alias_or_name', None)
-                if implicit_name and isinstance(implicit_name, str):
-                    out_name = implicit_name
-                    inner = proj
-                else:
-                    # Generate smart fallback names based on expression type
-                    s = str(proj).upper()
-                    if "HASHBYTES(" in s or "MD5(" in s: 
-                        out_name = "hash_expr"
-                    elif isinstance(proj, exp.Coalesce): 
-                        out_name = "coalesce_expr"
-                    elif isinstance(proj, (exp.Trim, exp.Upper, exp.Lower)): 
-                        col = proj.find(exp.Column)
-                        out_name = (col.name if col else "text_expr")
-                    elif isinstance(proj, (exp.Cast, exp.Convert)): 
-                        # For CAST, try to extract the source column name
-                        col = proj.find(exp.Column)
-                        out_name = (col.name if col else "cast_expr")
-                    elif isinstance(proj, exp.Column): 
-                        out_name = proj.name
-                    else: 
-                        out_name = "calc_expr"
-                    inner = proj
-
-            # Clean output name (remove comments/quotes, leading underscores)
-            out_name = self._clean_output_name(out_name) or f"col_{ordinal+1}"
-
-            # Collect input fields using enhanced resolution
-            inputs = self._collect_inputs_for_expr(inner, alias_map, derived_cols)
-            # Fallback: unqualified column with a single base table
-            if not inputs and isinstance(inner, exp.Column):
-                try:
-                    base_fqn = alias_map.get('')
-                    if base_fqn:
-                        db, sch, tbl = self._split_fqn(base_fqn)
-                        inputs = [
-                            ColumnReference(
-                                namespace=f"mssql://localhost/{(db or 'InfoTrackerDW').upper()}" if db else "mssql://localhost",
-                                table_name=f"{sch}.{tbl}",
-                                column_name=inner.name,
-                            )
-                        ]
-                except Exception:
-                    pass
-            # Fallback 2: simple identifier (e.g., [col]) with a single base table
-            if not inputs and isinstance(inner, exp.Identifier):
-                try:
-                    base_fqn = alias_map.get('')
-                    if base_fqn:
-                        db, sch, tbl = self._split_fqn(base_fqn)
-                        src_col = self._dequote(str(inner))
-                        inputs = [
-                            ColumnReference(
-                                namespace=f"mssql://localhost/{(db or 'InfoTrackerDW').upper()}" if db else "mssql://localhost",
-                                table_name=f"{sch}.{tbl}",
-                                column_name=src_col,
-                            )
-                        ]
-                except Exception:
-                    pass
-            
-            # Infer output type using enhanced type system
-            out_type = self._infer_type(inner, alias_map)
-            
-            # Determine transformation type
-            if isinstance(inner, (exp.Cast, exp.Convert)):
-                ttype = TransformationType.CAST
-            elif isinstance(inner, exp.Case):
-                ttype = TransformationType.CASE
-            elif isinstance(inner, exp.Column):
-                ttype = TransformationType.IDENTITY
-            else:
-                # IIF(...) bywa mapowane przez sqlglot do CASE; na wszelki wypadek:
-                s = str(inner).upper()
-                if s.startswith("CASE ") or s.startswith("CASEWHEN ") or s.startswith("IIF("):
-                    ttype = TransformationType.CASE
-                else:
-                    ttype = TransformationType.EXPRESSION
-
-
-            # Create lineage and schema entries
-            lineage.append(ColumnLineage(
-                output_column=out_name,
-                input_fields=inputs,
-                transformation_type=ttype,
-                transformation_description=self._short_desc(inner),
-            ))
-            output_columns.append(ColumnSchema(
-                name=out_name, 
-                data_type=out_type, 
-                nullable=True, 
-                ordinal=ordinal
-            ))
-            ordinal += 1
-        # Synthetic fallback: if no inputs were resolved but we have output columns and dependencies,
-        # create coarse lineage by linking each output column to each dependency table.
-        if not lineage and output_columns:
-            try:
-                deps = self._extract_dependencies(select_stmt) or set()
-            except Exception:
-                deps = set()
-            if deps:
-                refs_cache = []
-                for d in sorted(deps):
-                    parts = d.split('.')
-                    if len(parts) >= 3:
-                        db, sch, tbl = parts[0], parts[-2], parts[-1]
-                    elif len(parts) == 2:
-                        db = (self.current_database or self.default_database or 'InfoTrackerDW')
-                        sch, tbl = parts
-                    else:
-                        db = (self.current_database or self.default_database or 'InfoTrackerDW')
-                        sch, tbl = 'dbo', parts[0]
-                    refs_cache.append((f"mssql://localhost/{(db or 'InfoTrackerDW').upper()}", f"{sch}.{tbl}"))
-
-                new_lineage = []
-                for col in output_columns:
-                    inputs = [ColumnReference(namespace=ns, table_name=nm, column_name=col.name) for (ns, nm) in refs_cache]
-                    new_lineage.append(ColumnLineage(
-                        output_column=col.name,
-                        input_fields=inputs,
-                        transformation_type=TransformationType.EXPRESSION,
-                        transformation_description="synthetic dependency fallback"
-                    ))
-                lineage = new_lineage
-
-        return lineage, output_columns
+        from .parser_modules import select_lineage as _sl
+        return _sl._extract_column_lineage(self, stmt, view_name)
```

### SqlParser._extract_column_references
- DEV: `_extract_column_references(self, select_expr, select_stmt)` *(at dev_parser.py:5481)*
- NEW: `_extract_column_references(self, select_expr, select_stmt)` *(at parser.py:964)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_column_references']
- Calls removed: ['ColumnReference', '_get_table_name', '_ns_and_name', '_resolve_table_from_alias', 'append', 'endswith', 'find_all', 'hasattr', 'len', 'startswith', 'str']

```diff
--- DEV/dev_parser.py:5481
+++ NEW/parser.py:964
@@ -1,33 +1,3 @@
 def _extract_column_references(self, select_expr: exp.Expression, select_stmt: exp.Select) -> List[ColumnReference]:
-        """Extract column references from a SELECT expression."""
-        refs = []
-        
-        # Find all column references in the expression
-        for column_expr in select_expr.find_all(exp.Column):
-            table_name = "unknown"
-            column_name = str(column_expr.this)
-            
-            # Try to resolve table name from table reference or alias
-            if hasattr(column_expr, 'table') and column_expr.table:
-                table_alias = str(column_expr.table)
-                table_name = self._resolve_table_from_alias(table_alias, select_stmt)
-            else:
-                # If no table specified, try to infer from FROM clause
-                tables = []
-                for table in select_stmt.find_all(exp.Table):
-                    tables.append(self._get_table_name(table))
-                if len(tables) == 1:
-                    table_name = tables[0]
-            
-            # Filter out noise identifiers (variables, bracket-only token without dot, dynamic string concatenation)
-            if table_name and (table_name.startswith('@') or ('+' in table_name) or (table_name.startswith('[') and table_name.endswith(']') and '.' not in table_name)):
-                continue
-            if table_name != "unknown":
-                ns, nm = self._ns_and_name(table_name)
-                refs.append(ColumnReference(
-                    namespace=ns,
-                    table_name=nm,
-                    column_name=column_name
-                ))
-        
-        return refs
+        from .parser_modules import select_lineage as _sl
+        return _sl._extract_column_references(self, select_expr, select_stmt)
```

### SqlParser._extract_database_from_use_statement
- DEV: `_extract_database_from_use_statement(self, content)` *(at dev_parser.py:838)*
- NEW: `_extract_database_from_use_statement(self, content)` *(at parser.py:235)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_database_from_use_statement']
- Calls removed: ['_log_debug', 'group', 'match', 'split', 'startswith', 'strip']
- Regex removed: ['USE\\s+(?::([^:]+):|(?:\\[([^\\]]+)\\]|(\\w+)))']

```diff
--- DEV/dev_parser.py:838
+++ NEW/parser.py:235
@@ -1,20 +1,4 @@
 def _extract_database_from_use_statement(self, content: str) -> Optional[str]:
         """Extract database name from USE statement at the beginning of file."""
-        lines = content.strip().split('\n')
-        for line in lines[:10]:  # Check first 10 lines
-            line = line.strip()
-            if not line or line.startswith('--'):
-                continue
-            
-            # Match USE :DBNAME: or USE [database] or USE database
-            use_match = re.match(r'USE\s+(?::([^:]+):|(?:\[([^\]]+)\]|(\w+)))', line, re.IGNORECASE)
-            if use_match:
-                db_name = use_match.group(1) or use_match.group(2) or use_match.group(3)
-                self._log_debug(f"Found USE statement, setting database to: {db_name}")
-                return db_name
-            
-            # If we hit a non-comment, non-USE statement, stop looking
-            if not line.startswith(('USE', 'DECLARE', 'SET', 'PRINT')):
-                break
-        
-        return None
+        from .parser_modules import preprocess as _pp
+        return _pp._extract_database_from_use_statement(self, content)
```

### SqlParser._extract_dbt_model_name
- DEV: `_extract_dbt_model_name(self, sql_text)` *(at dev_parser.py:376)*
- NEW: `_extract_dbt_model_name(self, sql_text)` *(at parser.py:144)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_dbt_model_name']
- Calls removed: ['group', 'join', 'sanitize_name', 'search', 'split', 'splitlines', 'strip']
- Regex removed: ['(?im)^\\s*--\\s*dbt\\s+model:\\s*([A-Za-z0-9_\\.]+)']

```diff
--- DEV/dev_parser.py:376
+++ NEW/parser.py:144
@@ -1,17 +1,3 @@
 def _extract_dbt_model_name(self, sql_text: str) -> Optional[str]:
-        """Extract dbt model logical name from leading comment, e.g.:
-        -- dbt model: stg_orders
-        Returns lowercased sanitized name or None if not found.
-        """
-        try:
-            head = "\n".join(sql_text.splitlines()[:8])
-            m = re.search(r"(?im)^\s*--\s*dbt\s+model:\s*([A-Za-z0-9_\.]+)", head)
-            if m:
-                name = m.group(1).strip()
-                # Drop any dotted prefixes accidentally captured
-                name = name.split('.')[-1]
-                from .openlineage_utils import sanitize_name
-                return sanitize_name(name)
-        except Exception:
-            pass
-        return None
+        from .parser_modules import preprocess as _pp
+        return _pp._extract_dbt_model_name(self, sql_text)
```

### SqlParser._extract_dependencies
- DEV: `_extract_dependencies(self, stmt)` *(at dev_parser.py:2855)*
- NEW: `_extract_dependencies(self, stmt)` *(at parser.py:737)*
- **Body changed** (AST-hash)
- Calls removed: ['_canonical_temp_name', '_dequote', '_get_table_name', '_process_ctes', 'add', 'find_all', 'get', 'getattr', 'hasattr', 'isinstance', 'learn_from_references', 'lower', 'set', 'split', 'startswith', 'str', 'update']

```diff
--- DEV/dev_parser.py:2855
+++ NEW/parser.py:737
@@ -1,63 +1,3 @@
 def _extract_dependencies(self, stmt: exp.Expression) -> Set[str]:
-        """Extract table dependencies from SELECT or UNION statement including JOINs."""
-        dependencies = set()
-        
-        # Handle UNION at top level
-        if isinstance(stmt, exp.Union):
-            # Process both sides of the UNION
-            if isinstance(stmt.left, (exp.Select, exp.Union)):
-                dependencies.update(self._extract_dependencies(stmt.left))
-            if isinstance(stmt.right, (exp.Select, exp.Union)):
-                dependencies.update(self._extract_dependencies(stmt.right))
-            return dependencies
-        
-        # Must be SELECT from here
-        if not isinstance(stmt, exp.Select):
-            return dependencies
-            
-        select_stmt = stmt
-        
-        # Process CTEs first to build registry
-        self._process_ctes(select_stmt)
-        
-        # Use find_all to get all table references (FROM, JOIN, etc.)
-        for table in select_stmt.find_all(exp.Table):
-            table_name = self._get_table_name(table)
-            if table_name != "unknown":
-                # Learn references with explicit DB if available
-                try:
-                    if getattr(table, 'catalog', None):
-                        cat = self._dequote(str(table.catalog))
-                        if cat and cat.lower() not in {"view", "function", "procedure", "tempdb"} and self.registry:
-                            sch = str(table.db) if getattr(table, 'db', None) else 'dbo'
-                            nm = f"{self._dequote(sch)}.{self._dequote(table.name)}"
-                            self.registry.learn_from_references(nm, cat)
-                except Exception:
-                    pass
-                # Check if this is a CTE - if so, get its base dependencies instead
-                simple_name = table_name.split('.')[-1]
-                if simple_name in self.cte_registry:
-                    # This is a CTE reference - get dependencies from CTE definition
-                    with_clause = select_stmt.args.get('with')
-                    if with_clause and hasattr(with_clause, 'expressions'):
-                        for cte in with_clause.expressions:
-                            if hasattr(cte, 'alias') and str(cte.alias) == simple_name:
-                                if isinstance(cte.this, exp.Select):
-                                    cte_deps = self._extract_dependencies(cte.this)
-                                    dependencies.update(cte_deps)
-                                break
-                else:
-                    # Regular table dependency
-                    # Canonicalize temp tables to DB.schema.object.#temp so they appear distinctly
-                    if table_name.startswith('tempdb..#') or table_name.startswith('#'):
-                        dependencies.add(self._canonical_temp_name(table_name))
-                    else:
-                        dependencies.add(table_name)
-        
-        # Also check for subqueries and CTEs
-        for subquery in select_stmt.find_all(exp.Subquery):
-            if isinstance(subquery.this, exp.Select):
-                sub_deps = self._extract_dependencies(subquery.this)
-                dependencies.update(sub_deps)
-        
-        return dependencies
+        from .parser_modules import deps as _deps
+        return _deps._extract_dependencies(self, stmt)
```

### SqlParser._extract_first_create_statement
- DEV: `_extract_first_create_statement(self, sql_content, statement_type)` *(at dev_parser.py:4645)*
- NEW: `_extract_first_create_statement(self, sql_content, statement_type)` *(at parser.py:873)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_first_create_statement']
- Calls removed: ['group', 'search', 'strip']

```diff
--- DEV/dev_parser.py:4645
+++ NEW/parser.py:873
@@ -1,22 +1,3 @@
 def _extract_first_create_statement(self, sql_content: str, statement_type: str) -> str:
-        """Extract the first CREATE statement of the specified type."""
-        patterns = {
-            'FUNCTION': [
-                r'CREATE\s+(?:OR\s+ALTER\s+)?FUNCTION\s+.*?(?=CREATE\s+(?:OR\s+ALTER\s+)?(?:FUNCTION|PROCEDURE)|$)',
-                r'CREATE\s+FUNCTION\s+.*?(?=CREATE\s+(?:FUNCTION|PROCEDURE)|$)'
-            ],
-            'PROCEDURE': [
-                r'CREATE\s+(?:OR\s+ALTER\s+)?PROCEDURE\s+.*?(?=CREATE\s+(?:OR\s+ALTER\s+)?(?:FUNCTION|PROCEDURE)|$)',
-                r'CREATE\s+PROCEDURE\s+.*?(?=CREATE\s+(?:FUNCTION|PROCEDURE)|$)'
-            ]
-        }
-        
-        if statement_type not in patterns:
-            return ""
-        
-        for pattern in patterns[statement_type]:
-            match = re.search(pattern, sql_content, re.DOTALL | re.IGNORECASE)
-            if match:
-                return match.group(0).strip()
-        
-        return ""
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_first_create_statement(self, sql_content, statement_type)
```

### SqlParser._extract_function_name
- DEV: `_extract_function_name(self, sql_content)` *(at dev_parser.py:4526)*
- NEW: `_extract_function_name(self, sql_content)` *(at parser.py:835)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_function_name']
- Calls removed: ['group', 'search', 'strip', 'sub']
- Regex removed: ['CREATE\\s+(?:OR\\s+ALTER\\s+)?FUNCTION\\s+([^\\s\\(]+)', '[\\[\\]]']

```diff
--- DEV/dev_parser.py:4526
+++ NEW/parser.py:835
@@ -1,8 +1,4 @@
 def _extract_function_name(self, sql_content: str) -> Optional[str]:
-        """Extract function name from CREATE FUNCTION statement."""
-        match = re.search(r'CREATE\s+(?:OR\s+ALTER\s+)?FUNCTION\s+([^\s\(]+)', sql_content, re.IGNORECASE)
-        if not match:
-            return None
-        name = match.group(1).strip()
-        name = re.sub(r'[\[\]]', '', name)
-        return name
+        """Extract function name from CREATE FUNCTION statement (delegated)."""
+        from .parser_modules import functions as _func
+        return _func._extract_function_name(self, sql_content)
```

### SqlParser._extract_insert_into_columns
- DEV: `_extract_insert_into_columns(self, sql_content)` *(at dev_parser.py:4620)*
- NEW: `_extract_insert_into_columns(self, sql_content)` *(at parser.py:856)*
- **Body changed** (AST-hash)
- Calls removed: ['_dequote']
- Regex added: ['(?is)INSERT\\s+INTO\\s+[^\\s(]+\\s*\\((.*?)\\)']
- Regex removed: ['--.*?$', '/\\*.*?\\*/', 'INSERT\\s+INTO\\s+[^\\s(]+\\s*\\((.*?)\\)', '^_+']

```diff
--- DEV/dev_parser.py:4620
+++ NEW/parser.py:856
@@ -1,22 +1,14 @@
 def _extract_insert_into_columns(self, sql_content: str) -> list[str]:
-        m = re.search(r'INSERT\s+INTO\s+[^\s(]+\s*\((.*?)\)', sql_content, flags=re.IGNORECASE | re.DOTALL)
+        m = re.search(r'(?is)INSERT\s+INTO\s+[^\s(]+\s*\((.*?)\)', sql_content)
         if not m:
             return []
         inner = m.group(1)
         cols = []
         for raw in inner.split(','):
             col = raw.strip()
             # zbij aliasy i nawiasy, zostaw samą nazwę
             col = col.split('.')[-1]
-            # remove comments, quotes and leading underscores
-            try:
-                col = re.sub(r"/\*.*?\*/", "", col, flags=re.S)
-                col = re.sub(r"--.*?$", "", col, flags=re.M)
-            except Exception:
-                pass
-            col = self._dequote(col)
-            col = re.sub(r'^_+', '', col)
             col = re.sub(r'[^\w]', '', col)
             if col:
                 cols.append(col)
         return cols
```

### SqlParser._extract_insert_select_lineage_string
- DEV: `_extract_insert_select_lineage_string(self, sql_content, object_name)` *(at dev_parser.py:4060)*
- NEW: `_extract_insert_select_lineage_string(self, sql_content, object_name)` *(at parser.py:818)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_insert_select_lineage_string']
- Calls removed: ['ColumnLineage', 'ColumnReference', '_extract_basic_dependencies', '_extract_column_lineage', '_extract_dependencies', '_extract_insert_into_columns', '_normalize_tsql', '_strip_sql_comments', 'add', 'any', 'append', 'compile', 'escape', 'get', 'group', 'isinstance', 'len', 'next', 'parse', 'search', 'set', 'sorted', 'split', 'startswith', 'update', 'upper']
- Regex removed: ['INSERT\\s+INTO\\s+[^;]+?\\bSELECT\\b(.*?)(?=\\b(?:COMMIT|ROLLBACK|RETURN|END|GO|CREATE|ALTER|MERGE|UPDATE|DELETE|INSERT)\\b|$)', 'INSERT\\s+INTO\\s+[^;]+?\\bSELECT\\b(.*?);']

```diff
--- DEV/dev_parser.py:4060
+++ NEW/parser.py:818
@@ -1,95 +1,3 @@
 def _extract_insert_select_lineage_string(self, sql_content: str, object_name: str) -> tuple[List[ColumnLineage], Set[str]]:
-        """Extract column lineage and dependencies specifically for INSERT INTO ... SELECT statements in a procedure body.
-
-        Returns (lineage, dependencies). Uses only the SELECT that follows INSERT INTO.
-        """
-        lineage: List[ColumnLineage] = []
-        dependencies: Set[str] = set()
-
-        s = self._strip_sql_comments(self._normalize_tsql(sql_content))
-        # Try to capture the SELECT payload for INSERT INTO ... SELECT ... ;
-        m = re.search(r'INSERT\s+INTO\s+[^;]+?\bSELECT\b(.*?);', s, flags=re.IGNORECASE | re.DOTALL)
-        if not m:
-            # Looser fallback: up to next GO/COMMIT/RETURN/END or end of string
-            m = re.search(r'INSERT\s+INTO\s+[^;]+?\bSELECT\b(.*?)(?=\b(?:COMMIT|ROLLBACK|RETURN|END|GO|CREATE|ALTER|MERGE|UPDATE|DELETE|INSERT)\b|$)', s, flags=re.IGNORECASE | re.DOTALL)
-        if not m:
-            return lineage, dependencies
-
-        select_body = m.group(1)
-        select_sql = "SELECT " + select_body
-
-        try:
-            parsed = sqlglot.parse(select_sql, read=self.dialect)
-            if parsed and isinstance(parsed[0], exp.Select):
-                lineage, _out_cols = self._extract_column_lineage(parsed[0], object_name)
-                deps = self._extract_dependencies(parsed[0])
-            else:
-                deps = self._extract_basic_dependencies(select_sql)
-        except Exception:
-            deps = self._extract_basic_dependencies(select_sql)
-
-        # Merge canonical temps and base sources
-        expanded: Set[str] = set()
-        for d in deps:
-            parts = (d or '').split('.')
-            is_temp = any(seg.startswith('#') for seg in parts)
-            if is_temp:
-                # keep canonical temp
-                expanded.add(d)
-                simple = next((seg for seg in parts if seg.startswith('#')), parts[-1])
-                bases = self.temp_sources.get(simple)
-                if bases:
-                    expanded.update(bases)
-                else:
-                    # As a last resort, try to discover bases for this temp via a local string scan of SELECT ... INTO #temp
-                    try:
-                        patt = re.compile(r"(?is)SELECT\b.*?\bINTO\s+" + re.escape(simple) + r"\b(.*?)(?=;|\b(?:INSERT|UPDATE|DELETE|MERGE|CREATE|ALTER|END|GO)\b|$)")
-                        mm = patt.search(s)
-                        if mm:
-                            sel_into_sql = "SELECT " + mm.group(1)
-                            try:
-                                parsed_b = sqlglot.parse(sel_into_sql, read=self.dialect)
-                                if parsed_b and isinstance(parsed_b[0], exp.Select):
-                                    bases2 = self._extract_dependencies(parsed_b[0])
-                                else:
-                                    bases2 = self._extract_basic_dependencies(sel_into_sql)
-                            except Exception:
-                                bases2 = self._extract_basic_dependencies(sel_into_sql)
-                            for b in (bases2 or []):
-                                expanded.add(b)
-                    except Exception:
-                        pass
-            else:
-                expanded.add(d)
-        dependencies.update(expanded)
-
-        # If AST-based lineage failed but we have dependencies and INSERT column list,
-        # synthesize coarse column-level lineage so upstream appears in the graph.
-        if not lineage and dependencies:
-            try:
-                out_cols = self._extract_insert_into_columns(sql_content)
-            except Exception:
-                out_cols = []
-            if out_cols:
-                refs_cache = []
-                for d in sorted(dependencies):
-                    parts = (d or '').split('.')
-                    if len(parts) >= 3:
-                        db, sch, tbl = parts[0], parts[-2], parts[-1]
-                    elif len(parts) == 2:
-                        db = (self.current_database or self.default_database or 'InfoTrackerDW')
-                        sch, tbl = parts
-                    else:
-                        db = (self.current_database or self.default_database or 'InfoTrackerDW')
-                        sch, tbl = 'dbo', parts[0]
-                    refs_cache.append((f"mssql://localhost/{(db or 'InfoTrackerDW').upper()}", f"{sch}.{tbl}"))
-                for c in out_cols:
-                    inputs = [ColumnReference(namespace=ns, table_name=nm, column_name=c) for (ns, nm) in refs_cache]
-                    lineage.append(ColumnLineage(
-                        output_column=c,
-                        input_fields=inputs,
-                        transformation_type=TransformationType.EXPRESSION,
-                        transformation_description="synthetic dependency fallback from INSERT SELECT"
-                    ))
-
-        return lineage, dependencies
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_insert_select_lineage_string(self, sql_content, object_name)
```

### SqlParser._extract_materialized_output_from_procedure_string
- DEV: `_extract_materialized_output_from_procedure_string(self, sql_content)` *(at dev_parser.py:4157)*
- NEW: `_extract_materialized_output_from_procedure_string(self, sql_content)` *(at parser.py:823)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_materialized_output_from_procedure_string']
- Calls removed: ['ObjectInfo', 'TableSchema', '_get_full_table_name', '_normalize_table_ident', '_normalize_table_name_for_output', '_normalize_tsql', '_split_fqn', '_to_obj', 'finditer', 'group', 'join', 'len', 'lower', 'lstrip', 'rstrip', 'set', 'split', 'splitlines', 'startswith', 'strip', 'sub', 'upper']
- Regex removed: ['/\\*.*?\\*/', '\\bINSERT\\s+INTO\\s+([^\\s,()\\r\\n;]+)', '\\bSELECT\\s+.*?\\bINTO\\s+([^\\s,()\\r\\n;]+)']

```diff
--- DEV/dev_parser.py:4157
+++ NEW/parser.py:823
@@ -1,68 +1,3 @@
 def _extract_materialized_output_from_procedure_string(self, sql_content: str) -> Optional[ObjectInfo]:
-        """
-        Extract materialized output (SELECT INTO, INSERT INTO) from a procedure body.
-        - Zwraca ObjectInfo typu "table" z pełną nazwą DB.schema.table i poprawnym namespace.
-        - Nie używa _normalize_table_name_for_output (nie gubimy DB).
-        """
-        import re
-        from .models import ObjectInfo, TableSchema  # lokalny import dla pewności
-
-        # 1) Normalizacja i usunięcie komentarzy (żeby regexy nie łapały śmieci)
-        s = self._normalize_tsql(sql_content)
-        s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)  # block comments
-        lines = s.splitlines()
-        s = "\n".join(line for line in lines if not line.lstrip().startswith('--'))
-
-        # Helper: z tokena tabeli zbuduj pełną nazwę i namespace
-        def _to_obj(table_token: str) -> Optional[ObjectInfo]:
-            tok = (table_token or "").strip().rstrip(';')
-            # temp tables out
-            if tok.startswith('#') or tok.lower().startswith('tempdb..#'):
-                return None
-            # 1) znormalizuj identyfikator (zdejmij []/"")
-            norm = self._normalize_table_ident(tok)                  # np. EDW_CORE.dbo.LeadPartner_ref
-            # 2) pełna nazwa z DB (jeśli brak, dołóż current/default)
-            full_name = self._get_full_table_name(norm)              # -> DB.schema.table
-            # 3) namespace z DB
-            try:
-                db, sch, tbl = self._split_fqn(full_name)            # -> (DB, schema, table)
-            except Exception:
-                # awaryjnie: spróbuj rozbić ręcznie
-                parts = full_name.split('.')
-                if len(parts) == 3:
-                    db, sch, tbl = parts
-                elif len(parts) == 2:
-                    db = (self.current_database or self.default_database or "InfoTrackerDW")
-                    sch, tbl = parts
-                    full_name = f"{db}.{sch}.{tbl}"
-                else:
-                    db = (self.current_database or self.default_database or "InfoTrackerDW")
-                    sch = "dbo"
-                    tbl = parts[0]
-                    full_name = f"{db}.{sch}.{tbl}"
-            ns = f"mssql://localhost/{(db or (self.current_database or self.default_database or 'InfoTrackerDW')).upper()}"
-            # Normalize object key to schema.table for engine graph consistency
-            nm = self._normalize_table_name_for_output(full_name)
-
-            return ObjectInfo(
-                name=nm,
-                object_type="table",
-                schema=TableSchema(namespace=ns, name=nm, columns=[]),
-                lineage=[],
-                dependencies=set()
-            )
-
-        # 2) SELECT ... INTO <table>
-        #    (łapiemy pierwszy „persistent” match)
-        for m in re.finditer(r'\bSELECT\s+.*?\bINTO\s+([^\s,()\r\n;]+)', s, flags=re.IGNORECASE | re.DOTALL):
-            obj = _to_obj(m.group(1))
-            if obj:
-                return obj
-
-        # 3) INSERT INTO <table> [ (cols...) ] SELECT ...
-        for m in re.finditer(r'\bINSERT\s+INTO\s+([^\s,()\r\n;]+)', s, flags=re.IGNORECASE | re.DOTALL):
-            obj = _to_obj(m.group(1))
-            if obj:
-                return obj
-
-        return None
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_materialized_output_from_procedure_string(self, sql_content)
```

### SqlParser._extract_merge_lineage_string
- DEV: `_extract_merge_lineage_string(self, sql_content, procedure_name)` *(at dev_parser.py:2584)*
- NEW: `_extract_merge_lineage_string(self, sql_content, procedure_name)` *(at parser.py:722)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_merge_lineage_string']
- Calls removed: ['ColumnLineage', 'ColumnReference', 'ColumnSchema', '_extract_basic_dependencies', '_normalize_table_ident', '_ns_and_name', '_strip_sql_comments', '_transformation_for', 'add', 'append', 'endswith', 'enumerate', 'escape', 'finditer', 'get', 'group', 'len', 'lower', 'search', 'set', 'split', 'startswith', 'strip', 'update', 'upper', 'zip']
- Regex removed: ['(?i)\\b([A-Za-z_][\\w]*)\\.(?:\\[?([A-Za-z_][\\w]*)\\]?\\.)?\\[?([A-Za-z_][\\w]*)\\]?$', '(?i)\\b([A-Za-z_][\\w]*)\\b$', '(?i)\\b([A-Za-z_][\\w]*)\\s*\\.\\s*([A-Za-z_][\\w]*)\\b', '(?is)MERGE\\s+INTO\\s+([^\\s\\(,;]+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?', '(?is)SELECT\\s+.*?\\s+INTO\\s+(#\\w+)\\s+FROM\\s+([^\\s\\(,;]+(?:\\.[^\\s\\(,;]+)*)', '(?is)USING\\s+([^\\s\\(,;#]+|#\\w+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?', '(\\w+)$', 'WHEN\\s+MATCHED.*?THEN\\s+UPDATE\\s+SET\\s+(.*?)(?:WHEN\\s+|;|$)', 'WHEN\\s+NOT\\s+MATCHED\\s+BY\\s+TARGET\\s+THEN\\s+INSERT\\s*\\(([^)]*)\\)\\s*VALUES\\s*\\(([^)]*)\\)', '\\bCAST\\s*\\(', '\\bCOALESCE\\s*\\(', '\\bCONVERT\\s*\\(|\\bTRY_CAST\\s*\\(', '\\bISNULL\\s*\\(']

```diff
--- DEV/dev_parser.py:2584
+++ NEW/parser.py:722
@@ -1,158 +1,4 @@
 def _extract_merge_lineage_string(self, sql_content: str, procedure_name: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str], Optional[str]]:
-        """Parse MERGE INTO ... USING ... and try to build lineage.
-
-        Returns (lineage, output_columns, dependencies, target_table) where target_table is schema.table.
-        """
-        lineage: List[ColumnLineage] = []
-        output_columns: List[ColumnSchema] = []
-        dependencies: Set[str] = set()
-        target_table: Optional[str] = None
-
-        cleaned = self._strip_sql_comments(sql_content)
-        # Find MERGE INTO <target>
-        m_target = re.search(r'(?is)MERGE\s+INTO\s+([^\s\(,;]+)(?:\s+AS\s+(\w+)|\s+(\w+))?', cleaned)
-        if not m_target:
-            return lineage, output_columns, dependencies, None
-        target_raw = self._normalize_table_ident(m_target.group(1))
-        tgt_alias = (m_target.group(2) or m_target.group(3) or '').strip() or None
-        # Normalize to schema.table for output naming
-        target_parts = target_raw.split('.')
-        if len(target_parts) >= 3:
-            target_table = f"{target_parts[-2]}.{target_parts[-1]}"
-        elif len(target_parts) == 2:
-            target_table = target_raw
-        else:
-            target_table = f"dbo.{target_raw}"
-
-        # Find USING source (table or subquery or temp)
-        m_using = re.search(r'(?is)USING\s+([^\s\(,;#]+|#\w+)(?:\s+AS\s+(\w+)|\s+(\w+))?', cleaned)
-        source_name: Optional[str] = None
-        src_alias: Optional[str] = None
-        if m_using:
-            src = m_using.group(1).strip()
-            source_name = self._normalize_table_ident(src)
-            src_alias = (m_using.group(2) or m_using.group(3) or '').strip() or None
-
-        # If USING #temp, try to resolve temp -> base table via preceding SELECT ... INTO #temp FROM base
-        temp_to_base: dict[str, str] = {}
-        for m in re.finditer(r'(?is)SELECT\s+.*?\s+INTO\s+(#\w+)\s+FROM\s+([^\s\(,;]+(?:\.[^\s\(,;]+)*)', cleaned):
-            temp_to_base[self._normalize_table_ident(m.group(1))] = self._normalize_table_ident(m.group(2))
-        if source_name and (source_name.startswith('#') or source_name.lower().startswith('tempdb..#')):
-            base = temp_to_base.get(source_name) or temp_to_base.get(source_name.split('.')[-1])
-            if base:
-                source_name = base
-
-        # Helper: determine if a token refers to source/target alias or fully qualified table
-        def _match_col_ref(token: str) -> Optional[tuple[str, str]]:
-            t = token.strip()
-            # Strip CAST(...), COALESCE(...), HASHBYTES(...), functions and extract innards for first identifiable col
-            # Try explicit qualifier patterns first
-            m = re.search(r'(?i)\b([A-Za-z_][\w]*)\.(?:\[?([A-Za-z_][\w]*)\]?\.)?\[?([A-Za-z_][\w]*)\]?$', t)
-            if m:
-                alias_or_db, maybe_schema, col = m.group(1), m.group(2), m.group(3)
-                return alias_or_db.lower(), col
-            # Try alias.col in general expressions
-            m2 = re.search(r'(?i)\b([A-Za-z_][\w]*)\s*\.\s*([A-Za-z_][\w]*)\b', t)
-            if m2:
-                return m2.group(1).lower(), m2.group(2)
-            # Bare column name as last resort
-            m3 = re.search(r'(?i)\b([A-Za-z_][\w]*)\b$', t)
-            if m3:
-                return None, m3.group(1)
-            return None
-
-        # Detect transformation type hint from expression string
-        def _transformation_for(expr: str) -> TransformationType:
-            e = expr.upper()
-            if 'HASHBYTES' in e:
-                return TransformationType.EXPRESSION
-            if re.search(r'\bCAST\s*\(', e):
-                return TransformationType.CAST
-            if re.search(r'\bCONVERT\s*\(|\bTRY_CAST\s*\(', e):
-                return TransformationType.CAST
-            if re.search(r'\bCOALESCE\s*\(', e) or re.search(r'\bISNULL\s*\(', e):
-                return TransformationType.EXPRESSION
-            return TransformationType.IDENTITY
-
-        # Map UPDATE SET tgt.col = <expr>
-        update_block = re.search(r'WHEN\s+MATCHED.*?THEN\s+UPDATE\s+SET\s+(.*?)(?:WHEN\s+|;|$)', cleaned, flags=re.IGNORECASE | re.DOTALL)
-        assign_exprs: list[tuple[str, str]] = []  # (target_col, rhs_expr)
-        if update_block:
-            assigns_raw = update_block.group(1)
-            for a in re.split(r',\s*', assigns_raw):
-                left_alias_part = re.escape(tgt_alias) + r'\.|tgt\.|target\.|\w+\.' if tgt_alias else r'tgt\.|target\.|\w+\.'
-                pat = rf"\b(?:{left_alias_part})?(\w+)\s*=\s*(.+)$"
-                ma = re.search(pat, a.strip(), flags=re.IGNORECASE | re.DOTALL)
-                if ma:
-                    assign_exprs.append((ma.group(1), ma.group(2)))
-
-        # Map INSERT (cols...) VALUES (src.cols...)
-        insert_block = re.search(r'WHEN\s+NOT\s+MATCHED\s+BY\s+TARGET\s+THEN\s+INSERT\s*\(([^)]*)\)\s*VALUES\s*\(([^)]*)\)', cleaned, flags=re.IGNORECASE | re.DOTALL)
-        if insert_block:
-            cols = [c.strip() for c in insert_block.group(1).split(',') if c.strip()]
-            vals = [v.strip() for v in insert_block.group(2).split(',') if v.strip()]
-            for c, v in zip(cols, vals):
-                mc = re.search(r'(\w+)$', c)
-                if mc:
-                    assign_exprs.append((mc.group(1), v))
-
-        # Build output columns (union of left sides), keep order stable
-        seen = set()
-        for i, (t_col, _expr) in enumerate(assign_exprs):
-            if t_col not in seen:
-                output_columns.append(ColumnSchema(name=t_col, data_type=None, nullable=True, ordinal=i))
-                seen.add(t_col)
-
-        # Dependencies: add source_name if present
-        if source_name:
-            # Resolve temp source to base if it's temp
-            simple_src = source_name.split('.')[-1]
-            if simple_src in self.temp_registry:
-                # Try to find the SELECT INTO that created it and extract base deps from body
-                # Fallback: take dependencies from procedure body
-                deps_basic = self._extract_basic_dependencies(cleaned)
-                dependencies.update(d for d in deps_basic if not d.endswith(f".{target_table.split('.')[-1]}"))
-            else:
-                dependencies.add(source_name)
-
-        # Lineage edges: for each assignment, collect input column refs from expr
-        if target_table:
-            # Resolve default source dataset for alias references
-            ns_src_default, nm_src_default = (None, None)
-            if source_name:
-                ns_src_default, nm_src_default = self._ns_and_name(source_name)
-            for (t_col, expr) in assign_exprs:
-                refs: List[ColumnReference] = []
-                # collect all alias.col occurrences
-                for m in re.finditer(r'(?i)\b([A-Za-z_][\w]*)\s*\.\s*([A-Za-z_][\w]*)\b', expr):
-                    a, c = m.group(1).lower(), m.group(2)
-                    # if alias matches source alias, use default src dataset
-                    if src_alias and a == src_alias.lower():
-                        if ns_src_default and nm_src_default:
-                            refs.append(ColumnReference(namespace=ns_src_default, table_name=nm_src_default, column_name=c))
-                        continue
-                    if tgt_alias and a == tgt_alias.lower():
-                        # self-reference; skip as input
-                        continue
-                    # try treat as fully qualified table alias (fallback to default src)
-                    full_guess = a  # alias might actually be schema or table; best effort
-                    try:
-                        ns2, nm2 = self._ns_and_name(full_guess)
-                        refs.append(ColumnReference(namespace=ns2, table_name=nm2, column_name=c))
-                    except Exception:
-                        if ns_src_default and nm_src_default:
-                            refs.append(ColumnReference(namespace=ns_src_default, table_name=nm_src_default, column_name=c))
-                # If no alias.col found, try bare col name mapped to default source
-                if not refs and ns_src_default and nm_src_default:
-                    mlast = re.search(r'(?i)\b([A-Za-z_][\w]*)\b$', expr)
-                    if mlast:
-                        refs.append(ColumnReference(namespace=ns_src_default, table_name=nm_src_default, column_name=mlast.group(1)))
-                tt = _transformation_for(expr)
-                lineage.append(ColumnLineage(
-                    output_column=t_col,
-                    input_fields=refs,
-                    transformation_type=tt,
-                    transformation_description=f"MERGE expr: {t_col} = {expr.strip()}"
-                ))
-
-        return lineage, output_columns, dependencies, target_table
+        """Delegate to string fallback MERGE lineage extractor."""
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_merge_lineage_string(self, sql_content, procedure_name)
```

### SqlParser._extract_mstvf_lineage
- DEV: `_extract_mstvf_lineage(self, statement, function_name, output_columns)` *(at dev_parser.py:5222)*
- NEW: `_extract_mstvf_lineage(self, statement, function_name, output_columns)` *(at parser.py:944)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_mstvf_lineage']
- Calls removed: ['_extract_column_lineage', '_extract_dependencies', '_log_debug', 'extend', 'finditer', 'group', 'hasattr', 'isinstance', 'parse', 'set', 'str', 'strip', 'update']

```diff
--- DEV/dev_parser.py:5222
+++ NEW/parser.py:944
@@ -1,46 +1,3 @@
 def _extract_mstvf_lineage(self, statement: exp.Create, function_name: str, output_columns: List[ColumnSchema]) -> tuple[List[ColumnLineage], Set[str]]:
-        """Extract lineage from multi-statement table-valued function."""
-        lineage = []
-        dependencies = set()
-        
-        # Parse the entire function body to find all SQL statements
-        sql_text = str(statement)
-        
-        # Find INSERT, SELECT, UPDATE, DELETE statements
-        stmt_patterns = [
-            r'INSERT\s+INTO\s+@\w+.*?(?=(?:INSERT|SELECT|UPDATE|DELETE|RETURN|END|\Z))',
-            r'(?<!INSERT\s+INTO\s+@\w+.*?)SELECT\s+.*?(?=(?:INSERT|SELECT|UPDATE|DELETE|RETURN|END|\Z))',
-            r'UPDATE\s+.*?(?=(?:INSERT|SELECT|UPDATE|DELETE|RETURN|END|\Z))',
-            r'DELETE\s+.*?(?=(?:INSERT|SELECT|UPDATE|DELETE|RETURN|END|\Z))',
-            r'EXEC\s+.*?(?=(?:INSERT|SELECT|UPDATE|DELETE|RETURN|END|\Z))'
-        ]
-        
-        for pattern in stmt_patterns:
-            matches = re.finditer(pattern, sql_text, re.IGNORECASE | re.DOTALL)
-            for match in matches:
-                try:
-                    stmt_sql = match.group(0).strip()
-                    if not stmt_sql:
-                        continue
-                        
-                    # Parse the statement
-                    parsed_stmts = sqlglot.parse(stmt_sql, read=self.dialect)
-                    if parsed_stmts:
-                        for parsed_stmt in parsed_stmts:
-                            if isinstance(parsed_stmt, exp.Select):
-                                stmt_lineage, _ = self._extract_column_lineage(parsed_stmt, function_name)
-                                lineage.extend(stmt_lineage)
-                                stmt_deps = self._extract_dependencies(parsed_stmt)
-                                dependencies.update(stmt_deps)
-                            elif isinstance(parsed_stmt, exp.Insert):
-                                # Handle INSERT statements
-                                if hasattr(parsed_stmt, 'expression') and isinstance(parsed_stmt.expression, exp.Select):
-                                    stmt_lineage, _ = self._extract_column_lineage(parsed_stmt.expression, function_name)
-                                    lineage.extend(stmt_lineage)
-                                    stmt_deps = self._extract_dependencies(parsed_stmt.expression)
-                                    dependencies.update(stmt_deps)
-                except Exception as e:
-                    self._log_debug(f"Failed to parse statement in MSTVF: {e}")
-                    continue
-        
-        return lineage, dependencies
+        from .parser_modules import create_handlers as _ch
+        return _ch._extract_mstvf_lineage(self, statement, function_name, output_columns)
```

### SqlParser._extract_output_into_lineage_string
- DEV: `_extract_output_into_lineage_string(self, sql_content)` *(at dev_parser.py:4359)*
- NEW: `_extract_output_into_lineage_string(self, sql_content)` *(at parser.py:831)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_output_into_lineage_string']
- Calls removed: ['ColumnLineage', 'ColumnReference', 'ColumnSchema', '_clean_output_name', '_noise_token', '_normalize_table_ident', '_normalize_tsql', '_ns_and_name', '_split_expr_list', '_st', '_strip_sql_comments', 'add', 'append', 'endswith', 'enumerate', 'finditer', 'get', 'group', 'join', 'len', 'lower', 'max', 'search', 'set', 'split', 'startswith', 'strip', 'upper', 'values']
- Regex removed: ['(?i)\\b(?:inserted|deleted)\\s*\\.\\s*([A-Za-z_][\\w]*)', '(?i)\\b([A-Za-z_][\\w]*)\\s*\\.\\s*([A-Za-z_][\\w]*)\\b', '(?i)\\b(inserted|deleted)\\s*\\.\\s*([A-Za-z_][\\w]*)', '(?is)^(.*?)\\s+AS\\s+([\\w\\[\\]\\"\'`]+)$', '\\bCAST\\s*\\(|\\bCONVERT\\s*\\(|\\bTRY_CAST\\s*\\(', '\\bCOALESCE\\s*\\(|\\bISNULL\\s*\\(', '\\bDELETE\\s+FROM\\s+([^\\s(,;]+).*?\\bOUTPUT\\b\\s+(.*?)\\s+\\bINTO\\b\\s+([^\\s(,;]+)', '\\bFROM\\b(.*)$', '\\bFROM\\s+([^\\s,;()]+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?', '\\bINSERT\\s+INTO\\s+([^\\s(,;]+)[^;]*?\\bOUTPUT\\b\\s+(.*?)\\s+\\bINTO\\b\\s+([^\\s(,;]+)', '\\bJOIN\\s+([^\\s,;()]+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?', '\\bUPDATE\\s+([^\\s(,;]+).*?\\bOUTPUT\\b\\s+(.*?)\\s+\\bINTO\\b\\s+([^\\s(,;]+)']

```diff
--- DEV/dev_parser.py:4359
+++ NEW/parser.py:831
@@ -1,166 +1,3 @@
 def _extract_output_into_lineage_string(self, sql_content: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str], Optional[str]]:
-        """Parse INSERT/UPDATE/DELETE ... OUTPUT <exprs> INTO <target> and build lineage for the OUTPUT target.
-
-        Returns (lineage, output_columns, dependencies, output_target_table_name)
-        where output_target_table_name is schema.table.
-        """
-        lineage: List[ColumnLineage] = []
-        output_columns: List[ColumnSchema] = []
-        dependencies: Set[str] = set()
-        target_output: Optional[str] = None
-
-        s = self._strip_sql_comments(self._normalize_tsql(sql_content))
-
-        # Helper to normalize table -> schema.table
-        def _st(name: str) -> str:
-            name = self._normalize_table_ident(name)
-            parts = name.split('.')
-            if len(parts) >= 3:
-                return f"{parts[-2]}.{parts[-1]}"
-            if len(parts) == 2:
-                return name
-            return f"dbo.{name}"
-
-        # Try UPDATE ... OUTPUT ... INTO
-        m_upd = re.search(r'\bUPDATE\s+([^\s(,;]+).*?\bOUTPUT\b\s+(.*?)\s+\bINTO\b\s+([^\s(,;]+)', s, flags=re.IGNORECASE | re.DOTALL)
-        dml_type = None
-        dml_target = None
-        out_exprs = None
-        if m_upd:
-            dml_type = 'UPDATE'
-            dml_target = _st(m_upd.group(1))
-            out_exprs = m_upd.group(2)
-            target_output = _st(m_upd.group(3))
-        else:
-            # Try INSERT ... OUTPUT ... INTO
-            m_ins = re.search(r'\bINSERT\s+INTO\s+([^\s(,;]+)[^;]*?\bOUTPUT\b\s+(.*?)\s+\bINTO\b\s+([^\s(,;]+)', s, flags=re.IGNORECASE | re.DOTALL)
-            if m_ins:
-                dml_type = 'INSERT'
-                dml_target = _st(m_ins.group(1))
-                out_exprs = m_ins.group(2)
-                target_output = _st(m_ins.group(3))
-            else:
-                # Try DELETE ... OUTPUT ... INTO
-                m_del = re.search(r'\bDELETE\s+FROM\s+([^\s(,;]+).*?\bOUTPUT\b\s+(.*?)\s+\bINTO\b\s+([^\s(,;]+)', s, flags=re.IGNORECASE | re.DOTALL)
-                if m_del:
-                    dml_type = 'DELETE'
-                    dml_target = _st(m_del.group(1))
-                    out_exprs = m_del.group(2)
-                    target_output = _st(m_del.group(3))
-
-        if not dml_type or not out_exprs or not target_output:
-            return lineage, output_columns, dependencies, None
-
-        # Dependencies include DML target by default
-        dependencies.add(dml_target)
-
-        # For UPDATE, also gather FROM/JOIN sources for alias resolution
-        alias_map: Dict[str, str] = {}
-        if dml_type == 'UPDATE':
-            # Capture FROM tail for aliases
-            m_from = re.search(r'\bFROM\b(.*)$', s, flags=re.IGNORECASE | re.DOTALL)
-            if m_from:
-                from_tail = m_from.group(1)
-                def _noise_token(tok: str) -> bool:
-                    t = (tok or '').strip()
-                    return (t.startswith('@') or ('+' in t) or (t.startswith('[') and t.endswith(']') and '.' not in t))
-                for m in re.finditer(r'\bFROM\s+([^\s,;()]+)(?:\s+AS\s+(\w+)|\s+(\w+))?', ' ' + from_tail, flags=re.IGNORECASE | re.DOTALL):
-                    raw_tok = m.group(1)
-                    if _noise_token(raw_tok):
-                        continue
-                    tbl = self._normalize_table_ident(raw_tok)
-                    al = (m.group(2) or m.group(3) or '').strip()
-                    if al:
-                        alias_map[al.lower()] = tbl
-                    else:
-                        alias_map[tbl.split('.')[-1].lower()] = tbl
-                for m in re.finditer(r'\bJOIN\s+([^\s,;()]+)(?:\s+AS\s+(\w+)|\s+(\w+))?', from_tail, flags=re.IGNORECASE | re.DOTALL):
-                    raw_tok = m.group(1)
-                    if _noise_token(raw_tok):
-                        continue
-                    tbl = self._normalize_table_ident(raw_tok)
-                    al = (m.group(2) or m.group(3) or '').strip()
-                    if al:
-                        alias_map[al.lower()] = tbl
-                    else:
-                        alias_map[tbl.split('.')[-1].lower()] = tbl
-                for tbl in set(alias_map.values()):
-                    dependencies.add(tbl)
-
-        # Parse OUTPUT list: split by commas not inside parentheses (simple approach)
-        # Good enough for typical inserted.col, deleted.col, and simple expressions.
-        def _split_expr_list(t: str) -> List[str]:
-            items = []
-            depth = 0
-            buf = []
-            for ch in t:
-                if ch == '(':
-                    depth += 1
-                elif ch == ')':
-                    depth = max(0, depth - 1)
-                if ch == ',' and depth == 0:
-                    items.append(''.join(buf).strip())
-                    buf = []
-                else:
-                    buf.append(ch)
-            if buf:
-                items.append(''.join(buf).strip())
-            return items
-
-        exprs = _split_expr_list(out_exprs)
-
-        # Build columns and lineage
-        for idx, e in enumerate(exprs):
-            expr = e
-            # Optional AS alias for output column name
-            m_as = re.search(r"(?is)^(.*?)\s+AS\s+([\w\[\]\"'`]+)$", expr)
-            if m_as:
-                expr_core = m_as.group(1).strip()
-                out_name = self._clean_output_name(m_as.group(2))
-            else:
-                expr_core = expr
-                # Try derive from inserted/deleted.col
-                m_ic = re.search(r'(?i)\b(?:inserted|deleted)\s*\.\s*([A-Za-z_][\w]*)', expr_core)
-                out_name = m_ic.group(1) if m_ic else f"output_{idx+1}"
-
-            output_columns.append(ColumnSchema(name=out_name, data_type=None, nullable=True, ordinal=idx))
-
-            refs: List[ColumnReference] = []
-            # inserted/deleted references map to DML target table
-            for m in re.finditer(r'(?i)\b(inserted|deleted)\s*\.\s*([A-Za-z_][\w]*)', expr_core):
-                ns_t, nm_t = self._ns_and_name(dml_target)
-                refs.append(ColumnReference(namespace=ns_t, table_name=nm_t, column_name=m.group(2)))
-
-            # If UPDATE with FROM sources, also map alias.col refs
-            if dml_type == 'UPDATE' and alias_map:
-                for m in re.finditer(r'(?i)\b([A-Za-z_][\w]*)\s*\.\s*([A-Za-z_][\w]*)\b', expr_core):
-                    al = m.group(1).lower()
-                    col = m.group(2)
-                    base = alias_map.get(al)
-                    if base:
-                        ns, nm = self._ns_and_name(base)
-                        refs.append(ColumnReference(namespace=ns, table_name=nm, column_name=col))
-
-            # Fallback: if no refs detected, assume DML target self-ref
-            if not refs:
-                ns_t, nm_t = self._ns_and_name(dml_target)
-                refs.append(ColumnReference(namespace=ns_t, table_name=nm_t, column_name=out_name))
-
-            # Simple transformation typing using earlier helper
-            tt = TransformationType.IDENTITY
-            u = expr_core.upper()
-            if 'HASHBYTES' in u:
-                tt = TransformationType.EXPRESSION
-            elif re.search(r'\bCAST\s*\(|\bCONVERT\s*\(|\bTRY_CAST\s*\(', u):
-                tt = TransformationType.CAST
-            elif re.search(r'\bCOALESCE\s*\(|\bISNULL\s*\(', u):
-                tt = TransformationType.EXPRESSION
-
-            lineage.append(ColumnLineage(
-                output_column=out_name,
-                input_fields=refs,
-                transformation_type=tt,
-                transformation_description=f"OUTPUT expr: {expr_core.strip()}"
-            ))
-
-        return lineage, output_columns, dependencies, target_output
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_output_into_lineage_string(self, sql_content)
```

### SqlParser._extract_procedure_lineage
- DEV: `_extract_procedure_lineage(self, statement, procedure_name)` *(at dev_parser.py:5168)*
- NEW: `_extract_procedure_lineage(self, statement, procedure_name)` *(at parser.py:929)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_procedure_lineage']
- Calls removed: ['_extract_column_lineage', '_extract_dependencies', '_find_last_select_in_procedure', 'set']

```diff
--- DEV/dev_parser.py:5168
+++ NEW/parser.py:929
@@ -1,13 +1,4 @@
 def _extract_procedure_lineage(self, statement: exp.Create, procedure_name: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str]]:
         """Extract lineage from a procedure that returns a dataset."""
-        lineage = []
-        output_columns = []
-        dependencies = set()
-        
-        # Find the last SELECT statement in the procedure body
-        last_select = self._find_last_select_in_procedure(statement)
-        if last_select:
-            lineage, output_columns = self._extract_column_lineage(last_select, procedure_name)
-            dependencies = self._extract_dependencies(last_select)
-        
-        return lineage, output_columns, dependencies
+        from .parser_modules import create_handlers as _ch
+        return _ch._extract_procedure_lineage(self, statement, procedure_name)
```

### SqlParser._extract_procedure_lineage_string
- DEV: `_extract_procedure_lineage_string(self, sql_content, procedure_name)` *(at dev_parser.py:4579)*
- NEW: `_extract_procedure_lineage_string(self, sql_content, procedure_name)` *(at parser.py:852)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_procedure_lineage_string']
- Calls removed: ['_extract_basic_dependencies', '_extract_basic_lineage_from_select', '_extract_basic_select_columns', '_extract_column_lineage', '_extract_dependencies', '_find_last_select_string', 'group', 'isinstance', 'parse', 'search', 'set', 'update']
- Regex removed: ['INSERT\\s+INTO\\s+[^\\s(]+(?:\\s*\\([^)]*\\))?\\s+SELECT\\b(.*)$']

```diff
--- DEV/dev_parser.py:4579
+++ NEW/parser.py:852
@@ -1,40 +1,3 @@
 def _extract_procedure_lineage_string(self, sql_content: str, procedure_name: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str]]:
-        """Extract lineage from a procedure using string parsing."""
-        lineage = []
-        output_columns = []
-        dependencies = set()
-        m = re.search(r'INSERT\s+INTO\s+[^\s(]+(?:\s*\([^)]*\))?\s+SELECT\b(.*)$', sql_content, flags=re.IGNORECASE | re.DOTALL)
-        if m:
-            select_sql = "SELECT " + m.group(1)
-            try:
-                parsed = sqlglot.parse(select_sql, read=self.dialect)
-                if parsed and isinstance(parsed[0], exp.Select):
-                    lineage, output_columns = self._extract_column_lineage(parsed[0], procedure_name)
-                    deps = self._extract_dependencies(parsed[0])
-                    dependencies.update(deps)
-            except Exception:
-                # Fallback: chociaż dependencies ze string-parsera
-                dependencies.update(self._extract_basic_dependencies(select_sql))
-
-
-        # For procedures, extract dependencies from all SQL statements in the procedure body
-        # First try to find the last SELECT statement for lineage
-        last_select_sql = self._find_last_select_string(sql_content)
-        if last_select_sql:
-            try:
-                parsed = sqlglot.parse(last_select_sql, read=self.dialect)
-                if parsed and isinstance(parsed[0], exp.Select):
-                    lineage, output_columns = self._extract_column_lineage(parsed[0], procedure_name)
-                    dependencies = self._extract_dependencies(parsed[0])
-            except Exception:
-                # Fallback to basic analysis with string-based lineage
-                output_columns = self._extract_basic_select_columns(last_select_sql)
-                lineage = self._extract_basic_lineage_from_select(last_select_sql, output_columns, procedure_name)
-                dependencies = self._extract_basic_dependencies(last_select_sql)
-        
-        # Additionally, extract dependencies from the entire procedure body
-        # This catches tables used in SELECT INTO, JOIN, etc.
-        procedure_dependencies = self._extract_basic_dependencies(sql_content)
-        dependencies.update(procedure_dependencies)
-        
-        return lineage, output_columns, dependencies
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_procedure_lineage_string(self, sql_content, procedure_name)
```

### SqlParser._extract_procedure_name
- DEV: `_extract_procedure_name(self, sql_content)` *(at dev_parser.py:4535)*
- NEW: `_extract_procedure_name(self, sql_content)` *(at parser.py:840)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_procedure_name']
- Calls removed: ['group', 'search', 'strip', 'sub']
- Regex removed: ['CREATE\\s+(?:OR\\s+ALTER\\s+)?PROCEDURE\\s+([^\\s\\(]+)', '[\\[\\]]']

```diff
--- DEV/dev_parser.py:4535
+++ NEW/parser.py:840
@@ -1,8 +1,4 @@
 def _extract_procedure_name(self, sql_content: str) -> Optional[str]:
-        """Extract procedure name from CREATE PROCEDURE statement."""
-        match = re.search(r'CREATE\s+(?:OR\s+ALTER\s+)?PROCEDURE\s+([^\s\(]+)', sql_content, re.IGNORECASE)
-        if not match:
-            return None
-        name = match.group(1).strip()
-        name = re.sub(r'[\[\]]', '', name)
-        return name
+        """Extract procedure name from CREATE PROCEDURE statement (delegated)."""
+        from .parser_modules import procedures as _proc
+        return _proc._extract_procedure_name(self, sql_content)
```

### SqlParser._extract_procedure_outputs
- DEV: `_extract_procedure_outputs(self, statement)` *(at dev_parser.py:2495)*
- NEW: `_extract_procedure_outputs(self, statement)` *(at parser.py:718)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_procedure_outputs']
- Calls removed: ['ObjectInfo', 'TableSchema', '_is_insert_exec', '_is_select_into', '_normalize_table_name_for_output', '_parse_insert_exec', '_parse_insert_select', '_parse_select_into', 'any', 'append', 'findall', 'isinstance', 'lower', 'set', 'startswith', 'str', 'strip', 'upper', 'walk']

```diff
--- DEV/dev_parser.py:2495
+++ NEW/parser.py:718
@@ -1,88 +1,3 @@
 def _extract_procedure_outputs(self, statement: exp.Create) -> List[ObjectInfo]:
-        """Extract materialized outputs (SELECT INTO, INSERT INTO) from procedure body.
-
-        Prefer AST-based detection to capture both persistent and temp outputs with
-        correct lineage/dependencies. Falls back to light regex only if AST walk
-        fails, preserving previous behavior.
-        """
-        outputs: List[ObjectInfo] = []
-
-        # First try AST walk to find SELECT ... INTO and INSERT ... (SELECT|EXEC)
-        try:
-            for node in statement.walk():
-                # SELECT ... INTO ...
-                if isinstance(node, exp.Select) and self._is_select_into(node):
-                    try:
-                        obj = self._parse_select_into(node)
-                        if obj:
-                            outputs.append(obj)
-                    except Exception:
-                        pass
-                # INSERT ... (SELECT | EXEC)
-                elif isinstance(node, exp.Insert):
-                    try:
-                        if self._is_insert_exec(node):
-                            obj = self._parse_insert_exec(node)
-                        else:
-                            obj = self._parse_insert_select(node)
-                        if obj:
-                            outputs.append(obj)
-                    except Exception:
-                        pass
-        except Exception:
-            pass
-
-        if outputs:
-            return outputs
-
-        # Fallback to previous regex-based heuristic (persistent tables only)
-        sql_text = str(statement)
-
-        try:
-            # Look for SELECT ... INTO patterns
-            select_into_pattern = r'SELECT\s+.*?\s+INTO\s+([^\s,]+)'
-            select_into_matches = re.findall(select_into_pattern, sql_text, flags=re.IGNORECASE | re.DOTALL)
-            for table_match in select_into_matches:
-                table_name = table_match.strip()
-                # Skip temp tables in fallback
-                if not table_name.startswith('#') and 'tempdb' not in table_name.lower():
-                    normalized_name = self._normalize_table_name_for_output(table_name)
-                    db = self.current_database or self.default_database or "InfoTrackerDW"
-                    outputs.append(ObjectInfo(
-                        name=normalized_name,
-                        object_type="table",
-                        schema=TableSchema(
-                            namespace=f"mssql://localhost/{(db or 'InfoTrackerDW').upper()}",
-                            name=normalized_name,
-                            columns=[]
-                        ),
-                        lineage=[],
-                        dependencies=set()
-                    ))
-
-            # Look for INSERT INTO patterns (non-temp tables)
-            insert_into_pattern = r'INSERT\s+INTO\s+([^\s,\(]+)'
-            insert_into_matches = re.findall(insert_into_pattern, sql_text, flags=re.IGNORECASE)
-            for table_match in insert_into_matches:
-                table_name = table_match.strip()
-                # Skip temp tables in fallback
-                if not table_name.startswith('#') and 'tempdb' not in table_name.lower():
-                    normalized_name = self._normalize_table_name_for_output(table_name)
-                    # Avoid duplicates from SELECT INTO detection
-                    if not any(output.name == normalized_name for output in outputs):
-                        db = self.current_database or self.default_database or "InfoTrackerDW"
-                        outputs.append(ObjectInfo(
-                            name=normalized_name,
-                            object_type="table",
-                            schema=TableSchema(
-                                namespace=f"mssql://localhost/{db}",
-                                name=normalized_name,
-                                columns=[]
-                            ),
-                            lineage=[],
-                            dependencies=set()
-                        ))
-        except Exception:
-            pass
-
-        return outputs
+        from .parser_modules import create_handlers as _ch
+        return _ch._extract_procedure_outputs(self, statement)
```

### SqlParser._extract_select_from_return
- DEV: `_extract_select_from_return(self, statement)` *(at dev_parser.py:5182)*
- NEW: `_extract_select_from_return(self, statement)` *(at parser.py:934)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_select_from_return']
- Calls removed: ['group', 'isinstance', 'parse', 'search', 'str']
- Regex removed: ['RETURN\\s*\\(\\s*(SELECT.*?)\\s*\\)']

```diff
--- DEV/dev_parser.py:5182
+++ NEW/parser.py:934
@@ -1,14 +1,4 @@
 def _extract_select_from_return(self, statement: exp.Create) -> Optional[exp.Select]:
         """Extract SELECT statement from RETURN AS clause."""
-        # This is a simplified implementation - in practice would need more robust parsing
-        try:
-            sql_text = str(statement)
-            return_as_match = re.search(r'RETURN\s*\(\s*(SELECT.*?)\s*\)', sql_text, re.IGNORECASE | re.DOTALL)
-            if return_as_match:
-                select_sql = return_as_match.group(1)
-                parsed = sqlglot.parse(select_sql, read=self.dialect)
-                if parsed and isinstance(parsed[0], exp.Select):
-                    return parsed[0]
-        except Exception:
-            pass
-        return None
+        from .parser_modules import create_handlers as _ch
+        return _ch._extract_select_from_return(self, statement)
```

### SqlParser._extract_select_from_return_string
- DEV: `_extract_select_from_return_string(self, sql_content)` *(at dev_parser.py:4702)*
- NEW: `_extract_select_from_return_string(self, sql_content)` *(at parser.py:881)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_select_from_return_string']
- Calls removed: ['group', 'lstrip', 'search', 'startswith', 'strip', 'sub', 'upper']
- Regex removed: ['--.*?(?=\\n|$)', '/\\*.*?\\*/']

```diff
--- DEV/dev_parser.py:4702
+++ NEW/parser.py:881
@@ -1,42 +1,4 @@
 def _extract_select_from_return_string(self, sql_content: str) -> Optional[str]:
-        """Extract SELECT statement from RETURN clause using enhanced regex."""
-        # Remove comments first
-        cleaned_sql = re.sub(r'--.*?(?=\n|$)', '', sql_content, flags=re.MULTILINE)
-        cleaned_sql = re.sub(r'/\*.*?\*/', '', cleaned_sql, flags=re.DOTALL)
-        
-        # Updated patterns for different RETURN formats with better handling
-        patterns = [
-            # RETURNS TABLE AS RETURN (SELECT
-            r'RETURNS\s+TABLE\s+AS\s+RETURN\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # RETURNS TABLE RETURN (SELECT
-            r'RETURNS\s+TABLE\s+RETURN\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # RETURNS TABLE RETURN SELECT
-            r'RETURNS\s+TABLE\s+RETURN\s+(SELECT.*?)(?=[\s;]*(?:END|$))',
-            # RETURN AS \n (\n SELECT
-            r'RETURN\s+AS\s*\n\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # RETURN \n ( \n SELECT  
-            r'RETURN\s*\n\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # RETURN AS ( SELECT
-            r'RETURN\s+AS\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # RETURN ( SELECT
-            r'RETURN\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # AS \n RETURN \n ( \n SELECT
-            r'AS\s*\n\s*RETURN\s*\n\s*\(\s*(SELECT.*?)(?=\)[\s;]*(?:END|$))',
-            # RETURN SELECT (simple case)
-            r'RETURN\s+(SELECT.*?)(?=[\s;]*(?:END|$))',
-            # RETURN WITH ... SELECT ... (CTE before SELECT)
-            r'RETURN\s+(WITH\s+.*?SELECT[\s\S]*?)(?=[\s;]*(?:END|$))',
-            # Fallback - original pattern with end of string
-            r'RETURN\s*\(\s*(SELECT.*?)\s*\)(?:\s*;)?$'
-        ]
-        
-        for pattern in patterns:
-            match = re.search(pattern, cleaned_sql, re.DOTALL | re.IGNORECASE)
-            if match:
-                select_statement = match.group(1).strip()
-                # Check if it looks like a valid SELECT statement
-                up = select_statement.upper().lstrip()
-                if up.startswith('SELECT') or up.startswith('WITH'):
-                    return select_statement
-        
-        return None
+        """Extract SELECT statement from RETURN clause (delegated)."""
+        from .parser_modules import functions as _func
+        return _func._extract_select_from_return_string(self, sql_content)
```

### SqlParser._extract_table_aliases_from_select
- DEV: `_extract_table_aliases_from_select(self, select_sql)` *(at dev_parser.py:4889)*
- NEW: `_extract_table_aliases_from_select(self, select_sql)` *(at parser.py:903)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_table_aliases_from_select']
- Calls removed: ['findall', 'split', 'strip']

```diff
--- DEV/dev_parser.py:4889
+++ NEW/parser.py:903
@@ -1,20 +1,4 @@
 def _extract_table_aliases_from_select(self, select_sql: str) -> Dict[str, str]:
         """Extract table aliases from FROM and JOIN clauses."""
-        aliases = {}
-        
-        # Find FROM clause and all JOIN clauses
-        from_join_pattern = r'\b(?:FROM|JOIN)\s+([^\s]+)(?:\s+AS\s+)?(\w+)?'
-        matches = re.findall(from_join_pattern, select_sql, flags=re.IGNORECASE)
-        
-        for table_name, alias in matches:
-            clean_table = table_name.strip()
-            clean_alias = alias.strip() if alias else None
-            
-            if clean_alias:
-                aliases[clean_alias] = clean_table
-            else:
-                # If no alias, use the table name itself
-                table_short = clean_table.split('.')[-1]  # Get last part after dots
-                aliases[table_short] = clean_table
-                
-        return aliases
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_table_aliases_from_select(self, select_sql)
```

### SqlParser._extract_table_variable_schema
- DEV: `_extract_table_variable_schema(self, statement)` *(at dev_parser.py:5197)*
- NEW: `_extract_table_variable_schema(self, statement)` *(at parser.py:939)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_table_variable_schema']
- Calls removed: ['ColumnSchema', 'append', 'enumerate', 'group', 'len', 'search', 'split', 'str', 'strip']
- Regex removed: ['@\\w+\\s+TABLE\\s*\\((.*?)\\)']

```diff
--- DEV/dev_parser.py:5197
+++ NEW/parser.py:939
@@ -1,24 +1,4 @@
 def _extract_table_variable_schema(self, statement: exp.Create) -> List[ColumnSchema]:
         """Extract column schema from @table TABLE definition."""
-        # Simplified implementation - would need more robust parsing for production
-        output_columns = []
-        sql_text = str(statement)
-        
-        # Look for @Result TABLE (col1 type1, col2 type2, ...)
-        table_def_match = re.search(r'@\w+\s+TABLE\s*\((.*?)\)', sql_text, re.IGNORECASE | re.DOTALL)
-        if table_def_match:
-            columns_def = table_def_match.group(1)
-            # Parse column definitions
-            for i, col_def in enumerate(columns_def.split(',')):
-                col_parts = col_def.strip().split()
-                if len(col_parts) >= 2:
-                    col_name = col_parts[0].strip()
-                    col_type = col_parts[1].strip()
-                    output_columns.append(ColumnSchema(
-                        name=col_name,
-                        data_type=col_type,
-                        nullable=True,
-                        ordinal=i
-                    ))
-        
-        return output_columns
+        from .parser_modules import create_handlers as _ch
+        return _ch._extract_table_variable_schema(self, statement)
```

### SqlParser._extract_table_variable_schema_string
- DEV: `_extract_table_variable_schema_string(self, sql_content)` *(at dev_parser.py:4745)*
- NEW: `_extract_table_variable_schema_string(self, sql_content)` *(at parser.py:886)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_table_variable_schema_string']
- Calls removed: ['ColumnSchema', '_dequote', 'append', 'end', 'enumerate', 'group', 'join', 'len', 'match', 'search', 'strip']
- Regex removed: ['RETURNS\\s+@\\w+\\s+TABLE\\s*\\(', '\\s*(\\[[^\\]]+\\]|[A-Za-z_][\\w$#]*)\\s+((?:\\[[^\\]]+\\]|[A-Za-z_][\\w$]*)\\s*(?:\\([^)]*\\))?)']

```diff
--- DEV/dev_parser.py:4745
+++ NEW/parser.py:886
@@ -1,51 +1,4 @@
 def _extract_table_variable_schema_string(self, sql_content: str) -> List[ColumnSchema]:
-        """Extract column schema from RETURNS @var TABLE (...) with nested parens support."""
-        s = sql_content
-        # Find the position of "RETURNS @... TABLE ("
-        m = re.search(r'RETURNS\s+@\w+\s+TABLE\s*\(', s, flags=re.IGNORECASE | re.DOTALL)
-        if not m:
-            return []
-        start = m.end()  # position after the opening parenthesis
-        depth = 1
-        i = start
-        while i < len(s) and depth > 0:
-            ch = s[i]
-            if ch == '(':
-                depth += 1
-            elif ch == ')':
-                depth -= 1
-            i += 1
-        if depth != 0:
-            return []
-        columns_block = s[start:i-1]
-
-        # Split by commas at top level (ignore commas inside parentheses)
-        defs = []
-        buf = []
-        d = 0
-        for ch in columns_block:
-            if ch == '(':
-                d += 1
-            elif ch == ')':
-                d -= 1
-            if ch == ',' and d == 0:
-                defs.append(''.join(buf))
-                buf = []
-            else:
-                buf.append(ch)
-        if buf:
-            defs.append(''.join(buf))
-
-        cols: List[ColumnSchema] = []
-        for idx, raw in enumerate(defs):
-            col_def = raw.strip()
-            if not col_def:
-                continue
-            # Match: [name] TYPE or name TYPE(args)
-            m2 = re.match(r"\s*(\[[^\]]+\]|[A-Za-z_][\w$#]*)\s+((?:\[[^\]]+\]|[A-Za-z_][\w$]*)\s*(?:\([^)]*\))?)", col_def)
-            if not m2:
-                continue
-            name = self._dequote(m2.group(1))
-            dtype = m2.group(2).strip()
-            cols.append(ColumnSchema(name=name, data_type=dtype, nullable=True, ordinal=idx))
-        return cols
+        """Extract column schema from @table TABLE definition using regex."""
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_table_variable_schema_string(self, sql_content)
```

### SqlParser._extract_temp_name
- DEV: `_extract_temp_name(self, raw_name)` *(at dev_parser.py:211)*
- NEW: `_extract_temp_name(self, raw_name)` *(at parser.py:80)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_temp_name']
- Calls removed: ['group', 'match', 'split']
- Regex removed: ['([a-zA-Z0-9_]+)']

```diff
--- DEV/dev_parser.py:211
+++ NEW/parser.py:80
@@ -1,21 +1,3 @@
 def _extract_temp_name(self, raw_name: str) -> str:
-        """Extract clean temp table name from raw identifier.
-        
-        Handles cases like:
-        - '#tmp' → 'tmp'
-        - 'dbo.#tmp' → 'tmp'  
-        - '#tmp INTO' → 'tmp'
-        - '#tmp (' → 'tmp'
-        - '#tmp_COALESCE(x,y)' → 'tmp'
-        
-        Returns only valid identifier characters (alphanumeric + underscore).
-        """
-        if not raw_name or '#' not in raw_name:
-            return raw_name
-        
-        # Get part after last #
-        after_hash = raw_name.split('#')[-1]
-        
-        # Extract only valid identifier chars (stop at first non-identifier char)
-        match = re.match(r'([a-zA-Z0-9_]+)', after_hash)
-        return match.group(1) if match else after_hash
+        from .parser_modules import temp_utils as _tu
+        return _tu._extract_temp_name(self, raw_name)
```

### SqlParser._extract_tvf_lineage
- DEV: `_extract_tvf_lineage(self, statement, function_name)` *(at dev_parser.py:5120)*
- NEW: `_extract_tvf_lineage(self, statement, function_name)` *(at parser.py:924)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_tvf_lineage']
- Calls removed: ['_expand_dependency_to_base_tables', '_extract_column_lineage', '_extract_dependencies', '_extract_mstvf_lineage', '_extract_select_from_return', '_extract_table_variable_schema', '_extract_tvf_lineage_string', '_is_cte_reference', '_process_ctes', 'set', 'str', 'update', 'upper']

```diff
--- DEV/dev_parser.py:5120
+++ NEW/parser.py:924
@@ -1,47 +1,4 @@
 def _extract_tvf_lineage(self, statement: exp.Create, function_name: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str]]:
         """Extract lineage from a table-valued function."""
-        lineage = []
-        output_columns = []
-        dependencies = set()
-        
-        sql_text = str(statement)
-        
-        # Handle inline TVF (RETURN AS SELECT)
-        if "RETURN AS" in sql_text.upper() or "RETURN(" in sql_text.upper():
-            # Find the SELECT statement in the RETURN clause
-            select_stmt = self._extract_select_from_return(statement)
-            if select_stmt:
-                # Process CTEs first
-                self._process_ctes(select_stmt)
-                
-                # Extract lineage and expand dependencies
-                lineage, output_columns = self._extract_column_lineage(select_stmt, function_name)
-                raw_deps = self._extract_dependencies(select_stmt)
-                
-                # Expand CTEs and temp tables to base tables
-                for dep in raw_deps:
-                    expanded_deps = self._expand_dependency_to_base_tables(dep, select_stmt)
-                    dependencies.update(expanded_deps)
-        
-        # Handle multi-statement TVF (RETURN @table TABLE)
-        elif "RETURNS @" in sql_text.upper():
-            # Extract the table variable definition and find all statements
-            output_columns = self._extract_table_variable_schema(statement)
-            lineage, raw_deps = self._extract_mstvf_lineage(statement, function_name, output_columns)
-            
-            # Expand dependencies for multi-statement TVF
-            for dep in raw_deps:
-                expanded_deps = self._expand_dependency_to_base_tables(dep, statement)
-                dependencies.update(expanded_deps)
-        
-        # If AST-based extraction failed, fall back to string-based approach
-        if not dependencies and not lineage:
-            try:
-                lineage, output_columns, dependencies = self._extract_tvf_lineage_string(sql_text, function_name)
-            except Exception:
-                pass
-        
-        # Remove any CTE references from final dependencies
-        dependencies = {dep for dep in dependencies if not self._is_cte_reference(dep)}
-        
-        return lineage, output_columns, dependencies
+        from .parser_modules import create_handlers as _ch
+        return _ch._extract_tvf_lineage(self, statement, function_name)
```

### SqlParser._extract_tvf_lineage_string
- DEV: `_extract_tvf_lineage_string(self, sql_text, function_name)` *(at dev_parser.py:4668)*
- NEW: `_extract_tvf_lineage_string(self, sql_text, function_name)` *(at parser.py:877)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_tvf_lineage_string']
- Calls removed: ['_expand_dependency_to_base_tables', '_extract_basic_dependencies', '_extract_column_lineage', '_extract_dependencies', '_extract_select_from_return_string', '_process_ctes', 'parse', 'set', 'update']

```diff
--- DEV/dev_parser.py:4668
+++ NEW/parser.py:877
@@ -1,33 +1,3 @@
 def _extract_tvf_lineage_string(self, sql_text: str, function_name: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str]]:
-        """Extract TVF lineage using string-based approach as fallback."""
-        lineage = []
-        output_columns = []
-        dependencies = set()
-        
-        # Extract SELECT statement from RETURN clause using string patterns
-        select_string = self._extract_select_from_return_string(sql_text)
-        
-        if select_string:
-            try:
-                # Parse the extracted SELECT statement
-                statements = sqlglot.parse(select_string, dialect=sqlglot.dialects.TSQL)
-                if statements:
-                    select_stmt = statements[0]
-                    
-                    # Process CTEs first
-                    self._process_ctes(select_stmt)
-                    
-                    # Extract lineage and expand dependencies
-                    lineage, output_columns = self._extract_column_lineage(select_stmt, function_name)
-                    raw_deps = self._extract_dependencies(select_stmt)
-                    
-                    # Expand CTEs and temp tables to base tables
-                    for dep in raw_deps:
-                        expanded_deps = self._expand_dependency_to_base_tables(dep, select_stmt)
-                        dependencies.update(expanded_deps)
-            except Exception:
-                # If parsing fails, try basic string extraction
-                basic_deps = self._extract_basic_dependencies(sql_text)
-                dependencies.update(basic_deps)
-        
-        return lineage, output_columns, dependencies
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_tvf_lineage_string(self, sql_text, function_name)
```

### SqlParser._extract_update_from_lineage_string
- DEV: `_extract_update_from_lineage_string(self, sql_content)` *(at dev_parser.py:4226)*
- NEW: `_extract_update_from_lineage_string(self, sql_content)` *(at parser.py:827)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_update_from_lineage_string']
- Calls removed: ['ColumnLineage', 'ColumnReference', 'ColumnSchema', '_noise_token', '_normalize_table_ident', '_normalize_tsql', '_ns_and_name', '_strip_sql_comments', '_tt', 'add', 'append', 'endswith', 'enumerate', 'escape', 'finditer', 'get', 'group', 'items', 'len', 'lower', 'search', 'set', 'split', 'startswith', 'strip', 'upper', 'values']
- Regex removed: ['(?i)\\b([A-Za-z_][\\w]*)\\b$', '(?i)\\b([A-Za-z_][\\w]*)\\s*\\.\\s*([A-Za-z_][\\w]*)\\b', '(?is)\\bFROM\\s+([^\\s,;()]+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?', '(?is)\\bJOIN\\s+([^\\s,;()]+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?', '\\bCAST\\s*\\(|\\bCONVERT\\s*\\(|\\bTRY_CAST\\s*\\(', '\\bCOALESCE\\s*\\(|\\bISNULL\\s*\\(', '\\bUPDATE\\s+([^\\s\\(,;]+)(?:\\s+AS\\s+(\\w+)|\\s+(\\w+))?\\s+SET\\s+(.*?)\\bFROM\\b(.*)$']

```diff
--- DEV/dev_parser.py:4226
+++ NEW/parser.py:827
@@ -1,132 +1,3 @@
 def _extract_update_from_lineage_string(self, sql_content: str) -> tuple[List[ColumnLineage], List[ColumnSchema], Set[str], Optional[str]]:
-        """Parse UPDATE <target> [AS tgt] SET ... FROM <target> [AS tgt] JOIN <src> [AS src] ...
-        Returns (lineage, output_columns, dependencies, target_table_name)
-        target_table_name is schema.table.
-        """
-        lineage: List[ColumnLineage] = []
-        output_columns: List[ColumnSchema] = []
-        dependencies: Set[str] = set()
-        target_table: Optional[str] = None
-
-        s = self._strip_sql_comments(self._normalize_tsql(sql_content))
-        # Match UPDATE <target> [AS tgt]
-        m_upd = re.search(r'\bUPDATE\s+([^\s\(,;]+)(?:\s+AS\s+(\w+)|\s+(\w+))?\s+SET\s+(.*?)\bFROM\b(.*)$', s, flags=re.IGNORECASE | re.DOTALL)
-        if not m_upd:
-            return lineage, output_columns, dependencies, None
-        target_raw = self._normalize_table_ident(m_upd.group(1))
-        tgt_alias = (m_upd.group(2) or m_upd.group(3) or '').strip() or None
-        set_block = m_upd.group(4) or ''
-        from_tail = m_upd.group(5) or ''
-
-        # Collect FROM/JOIN sources and their aliases to resolve refs
-        alias_map: Dict[str, str] = {}
-        # Patterns like: FROM <tbl> [AS a] JOIN <tbl2> [AS b] ...
-        def _noise_token(tok: str) -> bool:
-            t = (tok or '').strip()
-            return (t.startswith('@') or ('+' in t) or (t.startswith('[') and t.endswith(']') and '.' not in t))
-        for m in re.finditer(r'(?is)\bFROM\s+([^\s,;()]+)(?:\s+AS\s+(\w+)|\s+(\w+))?', ' ' + from_tail):
-            raw_tok = m.group(1)
-            if _noise_token(raw_tok):
-                continue
-            tbl = self._normalize_table_ident(raw_tok)
-            al = (m.group(2) or m.group(3) or '').strip()
-            if al:
-                alias_map[al.lower()] = tbl
-            else:
-                # derive alias as last identifier
-                alias_map[tbl.split('.')[-1].lower()] = tbl
-        for m in re.finditer(r'(?is)\bJOIN\s+([^\s,;()]+)(?:\s+AS\s+(\w+)|\s+(\w+))?', from_tail):
-            raw_tok = m.group(1)
-            if _noise_token(raw_tok):
-                continue
-            tbl = self._normalize_table_ident(raw_tok)
-            al = (m.group(2) or m.group(3) or '').strip()
-            if al:
-                alias_map[al.lower()] = tbl
-            else:
-                alias_map[tbl.split('.')[-1].lower()] = tbl
-
-        # Normalize target to schema.table; if UPDATE used an alias, resolve it using alias_map
-        parts = target_raw.split('.')
-        if len(parts) >= 3:
-            target_table = f"{parts[-2]}.{parts[-1]}"
-        elif len(parts) == 2:
-            target_table = target_raw
-        else:
-            # If UPDATE used alias (e.g., UPDATE tgt), try to map it to real table from FROM/JOIN
-            guess = target_raw.lower()
-            real = alias_map.get(guess)
-            if real:
-                rparts = real.split('.')
-                target_table = f"{rparts[-2]}.{rparts[-1]}" if len(rparts) >= 2 else f"dbo.{real}"
-            else:
-                target_table = f"dbo.{target_raw}"
-
-        # Resolve default source for bare columns: prefer first non-target source
-        default_src = None
-        for al, tbl in alias_map.items():
-            if not tgt_alias or al != tgt_alias.lower():
-                default_src = tbl
-                break
-
-        # Helper: transformation type
-        def _tt(expr: str) -> TransformationType:
-            e = expr.upper()
-            if 'HASHBYTES' in e:
-                return TransformationType.EXPRESSION
-            if re.search(r'\bCAST\s*\(|\bCONVERT\s*\(|\bTRY_CAST\s*\(', e):
-                return TransformationType.CAST
-            if re.search(r'\bCOALESCE\s*\(|\bISNULL\s*\(', e):
-                return TransformationType.EXPRESSION
-            return TransformationType.IDENTITY
-
-        # Parse assignments: tgt.col = expr, comma-separated
-        assigns: List[tuple[str, str]] = []
-        for a in re.split(r',\s*', set_block):
-            a = a.strip()
-            if not a:
-                continue
-            # left may be tgt alias or table-qualified
-            ma = re.search(r'(?is)(?:' + (re.escape(tgt_alias) + r'\.|' if tgt_alias else '') + r'\w+\.)?(\w+)\s*=\s*(.+)$', a)
-            if not ma:
-                continue
-            assigns.append((ma.group(1), ma.group(2)))
-
-        # Build output columns (dedupe, keep order)
-        seen = set()
-        for i, (t_col, _expr) in enumerate(assigns):
-            if t_col not in seen:
-                output_columns.append(ColumnSchema(name=t_col, data_type=None, nullable=True, ordinal=i))
-                seen.add(t_col)
-
-        # Dependencies from alias map
-        for tbl in set(alias_map.values()):
-            dependencies.add(tbl)
-
-        # Build lineage from expressions, resolving alias.col
-        for (t_col, expr) in assigns:
-            refs: List[ColumnReference] = []
-            for m in re.finditer(r'(?i)\b([A-Za-z_][\w]*)\s*\.\s*([A-Za-z_][\w]*)\b', expr):
-                al = m.group(1).lower()
-                col = m.group(2)
-                if tgt_alias and al == tgt_alias.lower():
-                    # skip self refs
-                    continue
-                base = alias_map.get(al)
-                if base:
-                    ns, nm = self._ns_and_name(base)
-                    refs.append(ColumnReference(namespace=ns, table_name=nm, column_name=col))
-            # fallback: bare column -> default source
-            if not refs and default_src:
-                ns, nm = self._ns_and_name(default_src)
-                mlast = re.search(r'(?i)\b([A-Za-z_][\w]*)\b$', expr)
-                if mlast:
-                    refs.append(ColumnReference(namespace=ns, table_name=nm, column_name=mlast.group(1)))
-            lineage.append(ColumnLineage(
-                output_column=t_col,
-                input_fields=refs,
-                transformation_type=_tt(expr),
-                transformation_description=f"UPDATE expr: {t_col} = {expr.strip()}"
-            ))
-
-        return lineage, output_columns, dependencies, target_table
+        from .parser_modules import string_fallbacks as _sf
+        return _sf._extract_update_from_lineage_string(self, sql_content)
```

### SqlParser._extract_view_header_cols
- DEV: `_extract_view_header_cols(self, create_exp)` *(at dev_parser.py:757)*
- NEW: `_extract_view_header_cols(self, create_exp)` *(at parser.py:216)*
- **Body changed** (AST-hash)
- Calls added: ['_extract_view_header_cols']
- Calls removed: ['_collect', 'add', 'append', 'get', 'getattr', 'set', 'str', 'strip']

```diff
--- DEV/dev_parser.py:757
+++ NEW/parser.py:216
@@ -1,34 +1,3 @@
 def _extract_view_header_cols(self, create_exp) -> list[str]:
-        """Extract column names from CREATE VIEW (col1, col2, ...) AS pattern."""
-        cols: list[str] = []
-
-        def _collect(exprs) -> None:
-            if not exprs:
-                return
-            for e in exprs:
-                n = getattr(e, "name", None)
-                if n:
-                    cols.append(str(n).strip("[]"))
-                else:
-                    cols.append(str(e).strip().strip("[]"))
-
-        # 1) Some dialects attach header list directly on the CREATE node
-        exprs = getattr(create_exp, "expressions", None) or create_exp.args.get("expressions")
-        _collect(exprs)
-
-        # 2) Others attach it to the target (statement.this)
-        try:
-            target = getattr(create_exp, "this", None)
-            texprs = getattr(target, "expressions", None) or (getattr(target, "args", {}).get("expressions") if getattr(target, "args", None) else None)
-            _collect(texprs)
-        except Exception:
-            pass
-
-        # Deduplicate while preserving order
-        seen = set()
-        dedup_cols = []
-        for c in cols:
-            if c and c not in seen:
-                seen.add(c)
-                dedup_cols.append(c)
-        return dedup_cols
+        from .parser_modules import select_lineage as _sl
+        return _sl._extract_view_header_cols(self, create_exp)
```

_(diff limit reached — increase with --max-diffs)_

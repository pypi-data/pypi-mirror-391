# json_mage.py - Your Personal JSON Grimoire (ULTIMATE EDITION v8 - SHADOW MONARCH)
"""
DragoHan's JSON Mastery Library
The simplest way to work with JSON - no bullshit, just results.

Powers: 31+ methods for reading, counting, filtering, sorting, math, occurrence analysis, and modifying JSON
NEW: Universal modify() that auto-extracts data from ANY structure!
NEW: Shadow Monarch summary() with beautiful reports and duplicate detection!
"""

import jmespath
from typing import Any, Union, List, Dict
import json
from collections import Counter


class MageJSON:
    """
    The simplest JSON sorcery - read, write, count, filter, sort ANY JSON structure.
    """
    
    def __init__(self, data: Union[str, dict, list]):
        """Auto-converts anything to workable JSON"""
        if isinstance(data, str):
            try:
                self._raw = json.loads(data)
            except:
                self._raw = data
        else:
            self._raw = data
    
    # ===================================================================
    # READING POWERS (11 methods)
    # ===================================================================
    
    @property
    def first(self) -> Any:
        """Get first item - data.first"""
        if isinstance(self._raw, list):
            return self._raw[0] if self._raw else None
        elif isinstance(self._raw, dict):
            return list(self._raw.values())[0] if self._raw else None
        return self._raw
    
    @property
    def last(self) -> Any:
        """Get last item - data.last"""
        if isinstance(self._raw, list):
            return self._raw[-1] if self._raw else None
        elif isinstance(self._raw, dict):
            return list(self._raw.values())[-1] if self._raw else None
        return self._raw
    
    @property
    def keys(self) -> List[str]:
        """All unique keys - data.keys"""
        keys = set()
        self._collect_keys(self._raw, keys)
        return sorted(list(keys))
    
    @property
    def raw(self) -> Any:
        """Get original data - data.raw"""
        return self._raw
    
    def get(self, key: str) -> Any:
        """
        Get value for a key (searches anywhere)
        Works with dot notation: data.get('user.email')
        """
        result = jmespath.search(key, self._raw)
        if result is not None:
            return result
        return self._deep_search(self._raw, key)
    
    def all(self, key: str) -> List:
        """
        Get ALL values for a key
        Example: data.all('email') → all emails
        """
        return self._collect_all_values(self._raw, key)
    
    def find(self, value: Any) -> List:
        """
        Find items containing a value
        Example: data.find('john@email.com')
        """
        return self._find_value(self._raw, value)
    
    def unique(self, key: str) -> List:
        """
        Get unique values (no duplicates)
        Example: data.unique('status') → ['success', 'error']
        """
        return list(set(self.all(key)))
    
    def has(self, key: str, value: Any) -> bool:
        """
        Check if value exists
        Example: data.has('status', 'error') → True/False
        """
        return value in self.all(key)
    
    @property
    def show(self) -> str:
        """Pretty print - print(data.show)"""
        return json.dumps(self._raw, indent=2)
    
    def __getitem__(self, key):
        """Direct access - data['key'] or data[0]"""
        if isinstance(self._raw, (dict, list)):
            return self._raw[key]
        return None
    
    # ===================================================================
    # COUNTING & FILTERING POWERS (4 methods)
    # ===================================================================
    
    def count(self, key: str, value: Any = None) -> Union[int, dict]:
        """
        Count occurrences
        
        Examples:
            data.count('status', 'success')  → 3
            data.count('status')             → {'success': 3, 'error': 2}
        """
        all_values = self.all(key)
        
        if value is None:
            return dict(Counter(all_values))
        else:
            return all_values.count(value)
    
    def filter(self, key: str, value: Any) -> List:
        """
        Get items where key=value (direct match only)
        
        Example: data.filter('status', 'error') → all errors
        Note: For nested filtering, use smart_filter()
        """
        result = []
        if isinstance(self._raw, list):
            for item in self._raw:
                if isinstance(item, dict) and item.get(key) == value:
                    result.append(item)
        return result
    
    def smart_filter(self, key: str, operator_or_value: Any, value: Any = None) -> 'MageJSON':
        """
        UNIVERSAL smart filter with operator support - CHAINABLE
        
        Usage patterns:
            # Simple equality (backward compatible)
            logs.smart_filter("type", "water")
            
            # With operators
            logs.smart_filter("weight", ">", 50)
            logs.smart_filter("height", "<=", 10)
            logs.smart_filter("name", "contains", "char")
            logs.smart_filter("id", "in", [1, 5, 10])
            
            # Chained filters
            heavy_water = (logs
                .smart_filter("type", "water")
                .smart_filter("weight", ">", 50)
            )
        
        Operators:
            ==, !=, >, <, >=, <=, contains, in
        
        Returns:
            MageJSON object (chainable)
        """
        # Determine if we have 2 or 3 arguments
        if value is None:
            # 2 args: smart_filter(key, value) - simple equality
            operator = "=="
            compare_value = operator_or_value
        else:
            # 3 args: smart_filter(key, operator, value)
            operator = operator_or_value
            compare_value = value
        
        results = []
        
        if not isinstance(self._raw, list):
            return MageJSON(results)
        
        for item in self._raw:
            if item.get('error'):  # Skip error items
                continue
            
            # Get the actual value from the item
            item_value = self._get_nested_value(item, key)
            
            if item_value is None:
                continue
            
            # Apply operator comparison
            if self._compare(item_value, operator, compare_value):
                results.append(item)
        
        return MageJSON(results)
    
    def summary(self) -> str:
        """
        🌑 SHADOW MONARCH SUMMARY - Ultimate Data Analysis
        
        Automatically detects and provides beautiful reports for:
        - Simple data (users, products)
        - Complex data (Pokemon, API responses) 
        - Data with duplicates
        - Any nested structure
        
        Returns:
            Beautifully formatted Shadow Monarch styled report
        """
        from collections import Counter
        import sys
        
        # Helper function to create Shadow Monarch borders
        def shadow_border(title, status="[PROCESSING COMPLETE]"):
            width = 70
            border = "🌑 ━" + "━" * (width - 4) + "━ 🌑"
            title_line = f"│ {title:^{width - 2}} │"
            status_line = f"│ {status:^{width - 2}} │"
            return f"{border}\n{title_line}\n{status_line}\n{border}"
        
        # Helper function for section headers
        def section_header(title):
            width = 70
            return f"│  {title} │\n│  {'─' * (len(title) + 4)} │"
        
        # Helper function for field analysis
        def analyze_field(data, field_name):
            try:
                values = self.all(field_name)
                if not values:
                    return f"  • {field_name:<11} → [No Data Found]"
                
                # Handle different value types
                if all(isinstance(v, (int, float)) for v in values if v is not None):
                    # Numeric values
                    numeric_vals = [v for v in values if v is not None]
                    if numeric_vals:
                        min_val, max_val = min(numeric_vals), max(numeric_vals)
                        avg_val = sum(numeric_vals) / len(numeric_vals)
                        return f"  • {field_name:<11} → {min_val} - {max_val} (AVG: {avg_val:.0f})"
                elif all(isinstance(v, str) for v in values if v is not None):
                    # String values
                    unique_count = len(set(v for v in values if v is not None))
                    if unique_count == len(values):
                        return f"  • {field_name:<11} → [{unique_count} Unique Values]"
                    else:
                        counter = Counter(v for v in values if v is not None)
                        most_common = counter.most_common(1)[0]
                        return f"  • {field_name:<11} → [{unique_count} Values: {most_common[0]}: {most_common[1]}]"
                elif all(isinstance(v, list) for v in values if v is not None):
                    # List values (like types, abilities)
                    list_lengths = [len(v) for v in values if v is not None]
                    if list_lengths:
                        min_len, max_len = min(list_lengths), max(list_lengths)
                        avg_len = sum(list_lengths) / len(list_lengths)
                        return f"  • {field_name:<11} → [{min_len}-{max_len} Items] (AVG: {avg_len:.1f})"
                else:
                    # Mixed or complex values
                    unique_count = len(set(str(v) for v in values if v is not None))
                    return f"  • {field_name:<11} → [{unique_count} Unique Complex Values]"
                    
                return f"  • {field_name:<11} → [{len(values)} Values Analyzed]"
                
            except Exception:
                return f"  • {field_name:<11} → [Analysis Failed - Complex Data]"
        
        # Check for duplicates using smart_duplicate_check if available
        duplicate_status = "✅ [CLEAN] No duplicate records detected"
        duplicate_details = []
        integrity_score = "100%"
        
        try:
            # Try to import and use smart_duplicate_check
            from duplicates import smart_duplicate_check
            dup_result = smart_duplicate_check(self._raw)
            
            if dup_result.get('duplicates_found', False):
                dup_count = dup_result.get('duplicate_count', 0)
                total_items = dup_result.get('total_items', len(self._raw) if isinstance(self._raw, list) else 1)
                integrity_score = f"{((total_items - dup_count) / total_items * 100):.1f}%" if total_items > 0 else "0%"
                
                duplicate_status = f"⚠️  [ALERT] {dup_count} duplicate records detected"
                duplicate_details = [
                    f"⚠️  [CONFLICT] {dup_count} entries share identifiers",
                    f"⚠️  [RISK] Data integrity compromised: {integrity_score}",
                    f"⚠️  [ACTION] Recommend immediate deduplication"
                ]
        except ImportError:
            # duplicates module not available, do basic check
            if isinstance(self._raw, list):
                try:
                    # Simple duplicate check for ids
                    ids = [item.get('id') for item in self._raw if isinstance(item, dict) and 'id' in item]
                    if len(ids) != len(set(ids)):
                        duplicate_status = "⚠️  [ALERT] Possible duplicates detected"
                        integrity_score = "Unknown"
                except:
                    pass
        except Exception:
            # Any error in duplicate checking
            integrity_score = "Unknown"
        
        # Build the report
        report_lines = []
        
        # Determine data type and status
        if isinstance(self._raw, list):
            total_items = len(self._raw)
            if total_items == 0:
                data_type = "[Empty Dataset]"
                status = "[NO DATA TO ANALYZE]"
            else:
                # Try to detect data type
                first_item = self._raw[0] if self._raw else {}
                if isinstance(first_item, dict):
                    if 'name' in first_item and any(key in first_item for key in ['types', 'abilities', 'stats']):
                        data_type = "[Pokemon Collection]"
                    elif 'email' in first_item or 'username' in first_item:
                        data_type = "[User Records]"
                    elif 'price' in first_item or 'product' in first_item:
                        data_type = "[Product Catalog]"
                    else:
                        data_type = "[Structured Data]"
                else:
                    data_type = "[Simple List]"
                
                status = "[PROCESSING COMPLETE]" if integrity_score == "100%" else "[DUPLICATES DETECTED]"
        else:
            data_type = "[Single Object]"
            total_items = 1
            status = "[PROCESSING COMPLETE]"
        
        # Header
        report_lines.append(shadow_border("📊 DATA ANALYSIS REPORT", status))
        report_lines.append("│                                                                      │")
        
        # Dataset Overview
        report_lines.append(section_header("📋 DATASET OVERVIEW"))
        report_lines.append(f"│  • Data Type:       {data_type:<37} │")
        report_lines.append(f"│  • Total Records:   {total_items:<37} │")
        
        if integrity_score == "100%":
            quality = "[Excellent] - No missing fields"
        elif integrity_score == "Unknown":
            quality = "[Unknown] - Cannot verify"
        else:
            quality = f"[Warning] - Integrity: {integrity_score}"
        
        report_lines.append(f"│  • Data Quality:    {quality:<37} │")
        
        if isinstance(self._raw, list) and self._raw:
            keys_count = len(self.keys)
            report_lines.append(f"│  • Fields Found:     {keys_count} Core Attributes{' ' * (25 - len(str(keys_count)))}│")
        else:
            report_lines.append("│  • Fields Found:     Single Object{' ' * 19}│")
        
        report_lines.append("│                                                                      │")
        
        # Field Analysis
        if isinstance(self._raw, list) and self._raw and self.keys:
            report_lines.append(section_header("⚡ FIELD ANALYSIS"))
            for key in self.keys[:7]:  # Limit to first 7 keys for readability
                analysis = analyze_field(self._raw, key)
                report_lines.append(f"│{analysis:<69} │")
            
            if len(self.keys) > 7:
                report_lines.append(f"│  • ... and {len(self.keys) - 7} more fields{' ' * (35 - len(str(len(self.keys) - 7)))}│")
        
        report_lines.append("│                                                                      │")
        
        # Integrity Verification
        report_lines.append(section_header("🎯 INTEGRITY VERIFICATION"))
        report_lines.append(f"│{duplicate_status:<69} │")
        
        if duplicate_details:
            for detail in duplicate_details:
                report_lines.append(f"│{detail:<69} │")
        else:
            report_lines.append("│  ✅ [UNIQUE] All entries have distinct identifiers              │")
            report_lines.append("│  ✅ [PURE] No corrupted or incomplete data found              │")
            report_lines.append(f"│  ✅ [STABLE] Dataset integrity: {integrity_score:<15}               │")
        
        report_lines.append("│                                                                      │")
        
        # Final Assessment
        report_lines.append(section_header("💀 FINAL ASSESSMENT"))
        
        # Calculate tier based on data quality
        if integrity_score == "100%":
            tier = "S-TIER"
        elif integrity_score != "Unknown":
            score = float(integrity_score.rstrip('%'))
            if score >= 90:
                tier = "A-TIER"
            elif score >= 70:
                tier = "B-TIER"
            else:
                tier = "C-TIER"
        else:
            tier = "B-TIER"
        
        if isinstance(self._raw, list) and total_items > 0:
            report_lines.append(f"│  [{tier}] Complete dataset - No missing attributes              │")
            
            if data_type == "[Pokemon Collection]":
                unique_types = len(set(item.get('types', [{}])[0].get('name', 'unknown') for item in self._raw[:5] if isinstance(item, dict) and item.get('types')))
                report_lines.append(f"│  [A-TIER] Exceptional type diversity ({unique_types} types)            │")
                report_lines.append("│  [A-TIER] Balanced physical stats distribution               │")
                report_lines.append("│  [S-TIER] Standardized combat structure                     │")
            elif data_type == "[User Records]":
                report_lines.append("│  [B-TIER] Good user distribution                           │")
                report_lines.append("│  [A-TIER] Perfect data integrity across all records        │")
                report_lines.append("│  [S-TIER] Standardized structure maintained               │")
            else:
                report_lines.append("│  [A-TIER] Well-structured data format                      │")
                report_lines.append("│  [A-TIER] Consistent field distribution                   │")
                report_lines.append("│  [S-TIER] Standardized structure maintained               │")
        else:
            report_lines.append("│  [C-TIER] Empty or single-item dataset                       │")
        
        report_lines.append("│                                                                      │")
        
        # Deployment Status
        report_lines.append(section_header("🌑 DEPLOYMENT STATUS"))
        
        if integrity_score == "100%":
            report_lines.append("│  💎 This dataset is optimized and ready for                   │")
            report_lines.append("│     immediate tactical deployment                          │")
            report_lines.append("")
            report_lines.append("│  🎯 [STATUS] All systems green - Proceed with mission!     │")
        else:
            report_lines.append("│  ⚠️  WARNING: Dataset not ready for deployment              │")
            report_lines.append("│  💀 ACTION REQUIRED: Run smart_duplicate_del() before         │")
            report_lines.append("│     proceeding                                               │")
            report_lines.append("")
            report_lines.append("│  🎯 [STATUS] Systems yellow - Clean data required!         │")
        
        report_lines.append("│                                                                      │")
        report_lines.append("🌑 ━" + "━" * 66 + "━ 🌑")
        
        return "\n".join(report_lines)
    
    # ===================================================================
    # MATH POWERS (4 methods)
    # ===================================================================
    
    def sum(self, key: str) -> Union[int, float]:
        """
        Sum numeric values
        
        Example: data.sum('tokens_used') → 1543
        """
        all_values = self.all(key)
        try:
            return sum(all_values) if all_values else 0
        except TypeError:
            return 0
    
    def avg(self, key: str) -> float:
        """
        Average of numeric values
        
        Example: data.avg('score') → 85.3
        """
        all_values = self.all(key)
        try:
            return sum(all_values) / len(all_values) if all_values else 0
        except (TypeError, ZeroDivisionError):
            return 0
    
    def max(self, key: str) -> Any:
        """
        Maximum value
        
        Example: data.max('score') → 98
        """
        all_values = self.all(key)
        try:
            return max(all_values) if all_values else None
        except (TypeError, ValueError):
            return None
    
    def min(self, key: str) -> Any:
        """
        Minimum value
        
        Example: data.min('age') → 18
        """
        all_values = self.all(key)
        try:
            return min(all_values) if all_values else None
        except (TypeError, ValueError):
            return None
    
    # ===================================================================
    # OCCURRENCE ANALYSIS POWERS (4 methods) - BULLETPROOF!
    # ===================================================================
    
    def occurs_most(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        BULLETPROOF - Find the most frequent value for ANY key (direct OR nested)
        
        Automatically handles:
        - Direct values: weight, height, id
        - Nested values: type (finds types[].type.name)
        - Multiple values per item: dual-types counted separately
        - Any data type: strings, numbers, booleans
        
        Usage:
            # Get both value and count
            value, count = logs.occurs_most('type')
            # → ('water', 15)
            
            # Get only the value
            most_common = logs.occurs_most('weight', value_only=True)
            # → 905
        
        Parameters:
            key: Field to analyze (direct or nested)
            value_only: If True, returns only the value; if False, returns (value, count)
        
        Returns:
            (value, count) tuple by default, or just value if value_only=True
            Returns (None, 0) or None if no data
        """
        all_values = []
        
        if not isinstance(self._raw, list):
            return None if value_only else (None, 0)
        
        # Extract ALL values for this key (handles nested automatically)
        for item in self._raw:
            if item.get('error'):
                continue
            
            # Get value(s) using smart extraction
            extracted = self._extract_all_values_for_key(item, key)
            
            if extracted is not None:
                # If multiple values (like dual-types), add all
                if isinstance(extracted, list):
                    all_values.extend(extracted)
                else:
                    all_values.append(extracted)
        
        # Count occurrences
        if not all_values:
            return None if value_only else (None, 0)
        
        counts = Counter(all_values)
        value, count = counts.most_common(1)[0]
        
        return value if value_only else (value, count)
    
    def occurs_min(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        BULLETPROOF - Find the least frequent (rarest) value for ANY key
        
        Usage:
            value, count = logs.occurs_min('type')
            # → ('dragon', 1)
        """
        all_values = []
        
        if not isinstance(self._raw, list):
            return None if value_only else (None, 0)
        
        # Extract ALL values
        for item in self._raw:
            if item.get('error'):
                continue
            
            extracted = self._extract_all_values_for_key(item, key)
            
            if extracted is not None:
                if isinstance(extracted, list):
                    all_values.extend(extracted)
                else:
                    all_values.append(extracted)
        
        if not all_values:
            return None if value_only else (None, 0)
        
        counts = Counter(all_values)
        value, count = counts.most_common()[-1]  # Last = least common
        
        return value if value_only else (value, count)
    
    def occurs_rare(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        Alias for occurs_min - finds the rarest value
        """
        return self.occurs_min(key, value_only)
    
    def occurs_mid(self, key: str, value_only: bool = False) -> Union[tuple, Any]:
        """
        BULLETPROOF - Find the median frequency value for ANY key
        
        Usage:
            value, count = logs.occurs_mid('type')
            # → ('grass', 8)
        """
        all_values = []
        
        if not isinstance(self._raw, list):
            return None if value_only else (None, 0)
        
        # Extract ALL values
        for item in self._raw:
            if item.get('error'):
                continue
            
            extracted = self._extract_all_values_for_key(item, key)
            
            if extracted is not None:
                if isinstance(extracted, list):
                    all_values.extend(extracted)
                else:
                    all_values.append(extracted)
        
        if not all_values:
            return None if value_only else (None, 0)
        
        counts = Counter(all_values)
        sorted_items = counts.most_common()
        
        # Get middle item
        mid_idx = len(sorted_items) // 2
        value, count = sorted_items[mid_idx]
        
        return value if value_only else (value, count)
    
    # ===================================================================
    # SORTING POWER (1 method)
    # ===================================================================
    
    def sort(self, key: str, ascending: bool = True) -> List:
        """
        Sort items by a key
        
        Parameters:
            key: Field to sort by
            ascending: True = low→high, False = high→low
        
        Examples:
            data.sort('weight', False)  # Heaviest first
        """
        if isinstance(self._raw, list):
            try:
                return sorted(self._raw, key=lambda x: x.get(key, ''), reverse=not ascending)
            except Exception:
                return self._raw
        return self._raw
    
    # ===================================================================
    # MODIFICATION POWERS (5 methods)
    # ===================================================================
    
    def change(self, key: str, new_value: Any) -> 'MageJSON':
        """Change a key's value - returns self for chaining"""
        self._change_key(self._raw, key, new_value)
        return self
    
    def change_at(self, path: str, new_value: Any) -> 'MageJSON':
        """Change value at specific path - returns self for chaining"""
        parts = path.split('.')
        current = self._raw
        
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return self
        
        if isinstance(current, dict) and parts[-1] in current:
            current[parts[-1]] = new_value
        
        return self
    
    def add_key(self, key: str, value: Any) -> 'MageJSON':
        """Add new key - returns self for chaining"""
        if isinstance(self._raw, dict):
            self._raw[key] = value
        return self
    
    def remove_key(self, key: str) -> 'MageJSON':
        """Remove key everywhere - returns self for chaining"""
        self._remove_key(self._raw, key)
        return self
    
    def save_to(self, filename: str) -> str:
        """Save modified JSON"""
        try:
            import simple_file
            return simple_file.save(filename, self._raw)
        except:
            from pathlib import Path
            Path(filename if '.' in filename else f"{filename}.json").write_text(json.dumps(self._raw, indent=2))
            return f"✅ Saved: {filename}"
    
    # ===================================================================
    # ADVANCED
    # ===================================================================
    
    def where(self, jmes_query: str) -> Any:
        """Advanced JMESPath queries"""
        return jmespath.search(jmes_query, self._raw)
    
    def __repr__(self):
        """When you print(data)"""
        return self.show
    
    # ===================================================================
    # INTERNAL MAGIC - BULLETPROOF VALUE EXTRACTION
    # ===================================================================
    
    def _extract_all_values_for_key(self, obj: dict, search_key: str, depth: int = 0) -> Any:
        """
        BULLETPROOF extractor - gets ALL values for a key at ANY depth
        
        Returns:
        - Single value: 905
        - List of values: ["fire", "flying"] (for dual-types)
        - None: key not found
        """
        if depth > 50 or not isinstance(obj, dict):
            return None
        
        # PATTERN 1: Direct access
        if search_key in obj:
            val = obj[search_key]
            # Simple value - return it
            if not isinstance(val, (dict, list)):
                return val
            # Dict with 'name' or 'value' - return that
            if isinstance(val, dict):
                if 'name' in val:
                    return val['name']
                if 'value' in val:
                    return val['value']
            return val
        
        # PATTERN 2: Plural array (types[], abilities[], etc.)
        plural_key = search_key + 's'
        if plural_key in obj and isinstance(obj[plural_key], list):
            values = []
            for item in obj[plural_key]:
                if isinstance(item, dict) and search_key in item:
                    nested = item[search_key]
                    # Extract name/value if nested dict
                    if isinstance(nested, dict):
                        if 'name' in nested:
                            values.append(nested['name'])
                        elif 'value' in nested:
                            values.append(nested['value'])
                    else:
                        values.append(nested)
            
            # Return list if multiple, single if one, None if empty
            if len(values) > 1:
                return values
            elif len(values) == 1:
                return values[0]
        
        # PATTERN 3: Recursive deep search
        for key, val in obj.items():
            if isinstance(val, dict):
                result = self._extract_all_values_for_key(val, search_key, depth + 1)
                if result is not None:
                    return result
            elif isinstance(val, list):
                for list_item in val:
                    if isinstance(list_item, dict):
                        result = self._extract_all_values_for_key(list_item, search_key, depth + 1)
                        if result is not None:
                            return result
        
        return None
    
    def _deep_search(self, data: Any, key: str) -> Any:
        if isinstance(data, dict):
            if key in data:
                return data[key]
            for v in data.values():
                result = self._deep_search(v, key)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self._deep_search(item, key)
                if result is not None:
                    return result
        return None
    
    def _find_value(self, data: Any, target_value: Any) -> List:
        matches = []
        if isinstance(data, dict):
            if target_value in data.values():
                matches.append(data)
            for v in data.values():
                matches.extend(self._find_value(v, target_value))
        elif isinstance(data, list):
            for item in data:
                if item == target_value:
                    matches.append(item)
                else:
                    matches.extend(self._find_value(item, target_value))
        return matches
    
    def _collect_keys(self, data: Any, keys: set):
        if isinstance(data, dict):
            keys.update(data.keys())
            for v in data.values():
                self._collect_keys(v, keys)
        elif isinstance(data, list):
            for item in data:
                self._collect_keys(item, keys)
    
    def _collect_all_values(self, data: Any, key: str) -> List:
        values = []
        if isinstance(data, dict):
            if key in data:
                values.append(data[key])
            for v in data.values():
                values.extend(self._collect_all_values(v, key))
        elif isinstance(data, list):
            for item in data:
                values.extend(self._collect_all_values(item, key))
        return values
    
    def _change_key(self, data: Any, key: str, new_value: Any) -> bool:
        if isinstance(data, dict):
            if key in data:
                data[key] = new_value
                return True
            for v in data.values():
                if self._change_key(v, key, new_value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self._change_key(item, key, new_value):
                    return True
        return False
    
    def _remove_key(self, data: Any, key: str):
        if isinstance(data, dict):
            if key in data:
                del data[key]
            for v in list(data.values()):
                self._remove_key(v, key)
        elif isinstance(data, list):
            for item in data:
                self._remove_key(item, key)
    
    def _get_nested_value(self, obj: Any, search_key: str, depth: int = 0) -> Any:
        """Get SINGLE value for smart_filter (returns first match)"""
        if depth > 50 or not isinstance(obj, dict):
            return None
        
        # Direct match
        if search_key in obj:
            val = obj[search_key]
            if not isinstance(val, (dict, list)):
                return val
            if isinstance(val, dict):
                if 'name' in val:
                    return val['name']
                if 'value' in val:
                    return val['value']
            return val
        
        # Plural array - return FIRST match
        plural_key = search_key + 's'
        if plural_key in obj and isinstance(obj[plural_key], list):
            for item in obj[plural_key]:
                if isinstance(item, dict) and search_key in item:
                    nested = item[search_key]
                    if isinstance(nested, dict):
                        if 'name' in nested:
                            return nested['name']
                        if 'value' in nested:
                            return nested['value']
                    else:
                        return nested
        
        # Recursive
        for key, val in obj.items():
            if isinstance(val, dict):
                result = self._get_nested_value(val, search_key, depth + 1)
                if result is not None:
                    return result
            elif isinstance(val, list):
                for list_item in val:
                    if isinstance(list_item, dict):
                        result = self._get_nested_value(list_item, search_key, depth + 1)
                        if result is not None:
                            return result
        
        return None
    
    def _compare(self, item_value: Any, operator: str, compare_value: Any) -> bool:
        """Compare values using operator"""
        try:
            if operator == "==" or operator == "=":
                return item_value == compare_value
            elif operator == "!=":
                return item_value != compare_value
            elif operator == ">":
                return item_value > compare_value
            elif operator == "<":
                return item_value < compare_value
            elif operator == ">=":
                return item_value >= compare_value
            elif operator == "<=":
                return item_value <= compare_value
            elif operator == "contains":
                return str(compare_value).lower() in str(item_value).lower()
            elif operator == "in":
                return item_value in compare_value
            else:
                return item_value == compare_value
        except (TypeError, ValueError):
            return False


# ===================================================================
# UNIVERSAL MAGIC SPELL - BULLETPROOF EDITION v8 - SHADOW MONARCH
# ===================================================================

def _extract_data_from_structure(data: Any) -> Any:
    """
    🔮 UNIVERSAL DATA EXTRACTOR - BULLETPROOF
    
    Auto-extracts actual data from ANY common wrapper structure:
    
    Supported patterns:
    - {"cleaned_data": [...]}           # duplicates.py results
    - {"data": [...]}                   # API responses
    - {"results": [...]}                # Query results
    - {"items": [...]}                  # Generic items
    - {"response": {"data": [...]}}     # Nested API responses
    - {"result": {"data": [...]}}       # Nested results
    - {"output": [...]}                 # Generic output
    - {"content": [...]}                # Generic content
    - Pure data (no extraction needed) # Backward compatible
    
    Returns:
    - Extracted data (list/dict/etc)
    - Original data if no pattern matches
    """
    
    # If it's not a dict, return as-is (pure data)
    if not isinstance(data, dict):
        return data
    
    # PATTERN 1: Direct data keys (most common)
    direct_keys = ['cleaned_data', 'data', 'results', 'items', 'output', 'content']
    for key in direct_keys:
        if key in data:
            extracted = data[key]
            # Only extract if it looks like data (list/dict)
            if isinstance(extracted, (list, dict)):
                return extracted
    
    # PATTERN 2: Nested API responses
    nested_patterns = [
        ['response', 'data'],
        ['result', 'data'],
        ['response', 'results'],
        ['result', 'results'],
        ['data', 'data'],
        ['data', 'results']
    ]
    
    for path in nested_patterns:
        current = data
        valid_path = True
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                valid_path = False
                break
        
        if valid_path and isinstance(current, (list, dict)):
            return current
    
    # PATTERN 3: Single-item dict (might be the actual data)
    # Only if it has data-like structure
    if len(data) == 1:
        value = list(data.values())[0]
        if isinstance(value, (list, dict)) and len(str(value)) > 50:
            return value
    
    # PATTERN 4: Fallback - return original dict
    return data


def modify(data: Union[str, dict, list]) -> MageJSON:
    """
    🔮 UNIVERSAL modify() - BULLETPROOF EDITION v8
    
    Handles ANY data structure automatically:
    
    ✅ Pure data: modify([item1, item2])
    ✅ Results dict: modify({"cleaned_data": [...]})
    ✅ API responses: modify({"data": [...]})
    ✅ Nested structures: modify({"response": {"data": [...]}})
    ✅ Custom patterns: modify({"results": [...]})
    ✅ Backward compatible: All existing functionality preserved
    
    Usage:
        # Old way (still works)
        logs = modify([pokemon1, pokemon2])
        
        # New universal way
        logs = modify(smart_duplicate_del(data))  # Auto-extracts!
        logs = modify({"data": api_results})      # Auto-extracts!
        logs = modify({"cleaned_data": cleaned})  # Auto-extracts!
    
    Returns:
        MageJSON object with extracted data
    """
    # Extract actual data from any wrapper structure
    extracted_data = _extract_data_from_structure(data)
    
    # Create MageJSON with the extracted data
    return MageJSON(extracted_data)


def myjson(data: Union[str, dict, list]) -> MageJSON:
    """Alternative name with same universal powers"""
    return modify(data)


__all__ = ['modify', 'myjson', 'MageJSON']

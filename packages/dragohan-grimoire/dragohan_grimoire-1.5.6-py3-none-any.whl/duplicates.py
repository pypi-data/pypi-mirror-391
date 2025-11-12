"""
🔮 DUPLICATES SPELL - Ultimate Grimoire Module

One-liner duplicate detection and removal for ANY data structure!

QUICK START:
    from duplicates import *
    
    # Auto-discover and analyze ANY data:
    smart_duplicate_check(load("your_data"))
    
    # Manual control:
    logs = modify(your_data)
    logs.duplicate_check("id")
    logs.del_duplicate("id")

FEATURES:
✅ Auto-discovers data structure
✅ Works with nested keys (dot notation)
✅ Handles ANY data type
✅ Beautiful JSON output
✅ Smart recommendations
✅ Zero manual configuration needed

USE CASES:
- Pokemon data: smart_duplicate_check(load("pokemon"))
- User data: smart_duplicate_check(load("users"))
- API responses: smart_duplicate_check(get.many(urls))
- Unknown data: smart_duplicate_check(load("mystery_file"))
- Any JSON/list structure

Created by: Cascade AI | For: Dragohan Grimoire | Version: 2.0
"""

import json
from collections import Counter
from typing import Any, Union, List, Dict


class DuplicateChecker:
    """Enhanced wrapper for duplicate detection and removal in complex data structures"""
    
    def __init__(self, data: Any):
        self._data = data
        self._raw = data
    
    @property
    def raw(self):
        """Return the raw data"""
        return self._raw
    
    def _flatten_values(self, data: Any, parent_key: str = '') -> List[tuple]:
        """Recursively flatten nested structures to extract all key-value pairs"""
        items = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                if isinstance(value, (dict, list)):
                    items.extend(self._flatten_values(value, new_key))
                else:
                    items.append((new_key, value))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                new_key = f"{parent_key}[{idx}]" if parent_key else f"[{idx}]"
                if isinstance(item, (dict, list)):
                    items.extend(self._flatten_values(item, new_key))
                else:
                    items.append((parent_key, item))
        
        return items
    
    def _serialize_item(self, item: Any) -> str:
        """Convert item to a hashable string for comparison"""
        if isinstance(item, (dict, list)):
            return json.dumps(item, sort_keys=True)
        return str(item)
    
    def duplicate_check(self, key: str = None) -> Dict[str, Any]:
        """
        Check for duplicates in the data structure
        
        Args:
            key: Optional key to check duplicates for (works with nested keys using dot notation)
        
        Returns:
            Dictionary with duplicate information in JSON format
        """
        result = {
            "duplicates_found": False,
            "total_items": 0,
            "unique_items": 0,
            "duplicate_count": 0,
            "details": []
        }
        
        if not self._data:
            print("no duplicates found ✅")
            return result
        
        # Handle list of items
        if isinstance(self._data, list):
            result["total_items"] = len(self._data)
            
            if key:
                # Check duplicates for a specific key
                values = []
                for item in self._data:
                    if isinstance(item, dict):
                        # Handle nested keys
                        keys = key.split('.')
                        value = item
                        try:
                            for k in keys:
                                value = value[k]
                            values.append(self._serialize_item(value))
                        except (KeyError, TypeError):
                            continue
                    else:
                        values.append(self._serialize_item(item))
                
                counter = Counter(values)
                duplicates = {k: v for k, v in counter.items() if v > 1}
                
                if duplicates:
                    result["duplicates_found"] = True
                    result["unique_items"] = len(counter)
                    result["duplicate_count"] = sum(v - 1 for v in duplicates.values())
                    
                    for value, count in duplicates.items():
                        result["details"].append({
                            "key": key,
                            "value": value,
                            "occurrences": count,
                            "excess_copies": count - 1
                        })
            else:
                # Check entire items for duplicates
                serialized = [self._serialize_item(item) for item in self._data]
                counter = Counter(serialized)
                duplicates = {k: v for k, v in counter.items() if v > 1}
                
                if duplicates:
                    result["duplicates_found"] = True
                    result["unique_items"] = len(counter)
                    result["duplicate_count"] = sum(v - 1 for v in duplicates.values())
                    
                    for value, count in duplicates.items():
                        try:
                            parsed = json.loads(value)
                        except:
                            parsed = value
                        
                        result["details"].append({
                            "item": parsed,
                            "occurrences": count,
                            "excess_copies": count - 1
                        })
        
        elif isinstance(self._data, dict):
            # For dictionaries, check duplicate values
            values = list(self._data.values())
            serialized = [self._serialize_item(v) for v in values]
            counter = Counter(serialized)
            duplicates = {k: v for k, v in counter.items() if v > 1}
            
            result["total_items"] = len(values)
            
            if duplicates:
                result["duplicates_found"] = True
                result["unique_items"] = len(counter)
                result["duplicate_count"] = sum(v - 1 for v in duplicates.values())
                
                for value, count in duplicates.items():
                    keys_with_value = [k for k, v in self._data.items() 
                                      if self._serialize_item(v) == value]
                    
                    try:
                        parsed = json.loads(value)
                    except:
                        parsed = value
                    
                    result["details"].append({
                        "value": parsed,
                        "keys": keys_with_value,
                        "occurrences": count,
                        "excess_copies": count - 1
                    })
        
        # Print result
        if result["duplicates_found"]:
            print(json.dumps(result, indent=2))
        else:
            print("no duplicates found ✅")
        
        return result
    
    def del_duplicate(self, key: str = None) -> Any:
        """
        Remove duplicates from the data structure
        
        Args:
            key: Optional key to deduplicate by (works with nested keys using dot notation)
        
        Returns:
            Data with duplicates removed
        """
        if not self._data:
            print("no duplicates found ✅")
            return self._data
        
        # Handle list of items
        if isinstance(self._data, list):
            if key:
                # Remove duplicates based on specific key
                seen = set()
                unique_items = []
                
                for item in self._data:
                    if isinstance(item, dict):
                        # Handle nested keys
                        keys = key.split('.')
                        value = item
                        try:
                            for k in keys:
                                value = value[k]
                            serialized = self._serialize_item(value)
                            
                            if serialized not in seen:
                                seen.add(serialized)
                                unique_items.append(item)
                        except (KeyError, TypeError):
                            unique_items.append(item)
                    else:
                        serialized = self._serialize_item(item)
                        if serialized not in seen:
                            seen.add(serialized)
                            unique_items.append(item)
                
                removed = len(self._data) - len(unique_items)
                self._data = unique_items
                self._raw = unique_items
                
                if removed > 0:
                    print(f"✅ Removed {removed} duplicate(s). {len(unique_items)} unique items remaining.")
                else:
                    print("no duplicates found ✅")
            else:
                # Remove complete duplicate items
                seen = set()
                unique_items = []
                
                for item in self._data:
                    serialized = self._serialize_item(item)
                    if serialized not in seen:
                        seen.add(serialized)
                        unique_items.append(item)
                
                removed = len(self._data) - len(unique_items)
                self._data = unique_items
                self._raw = unique_items
                
                if removed > 0:
                    print(f"✅ Removed {removed} duplicate(s). {len(unique_items)} unique items remaining.")
                else:
                    print("no duplicates found ✅")
        
        elif isinstance(self._data, dict):
            # For dictionaries, remove keys with duplicate values
            seen = set()
            unique_dict = {}
            removed = 0
            
            for k, v in self._data.items():
                serialized = self._serialize_item(v)
                if serialized not in seen:
                    seen.add(serialized)
                    unique_dict[k] = v
                else:
                    removed += 1
            
            self._data = unique_dict
            self._raw = unique_dict
            
            if removed > 0:
                print(f"✅ Removed {removed} duplicate value(s). {len(unique_dict)} unique entries remaining.")
            else:
                print("no duplicates found ✅")
        
        return self._data
    
    def show(self):
        """Display the current data in pretty JSON format"""
        print(json.dumps(self._data, indent=2))
        return self._data


def auto_discover_keys(data, max_depth=3):
    """Automatically discover potential keys for duplicate checking"""
    if not data or not isinstance(data, list):
        return []
    
    keys = set()
    
    def extract_keys(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_path = f"{path}.{key}" if path else key
                
                # Add this key if it looks like an identifier
                if any(keyword in key.lower() for keyword in ['id', 'uuid', 'key', 'name', 'code', 'slug']):
                    keys.add(full_path)
                
                # Recurse for nested objects (limit depth)
                if isinstance(value, dict) and len(full_path.split('.')) < max_depth:
                    extract_keys(value, full_path)
    
    # Sample first few items to discover keys
    for item in data[:5]:
        extract_keys(item)
    
    return sorted(list(keys))

def smart_duplicate_check(data):
    """
    🔮 ULTIMATE DUPLICATE CHECKER - One-liner magic!
    
    Automatically discovers data structure and finds duplicates.
    Works on ANY data without manual configuration.
    
    Usage:
        smart_duplicate_check(load("data"))
        smart_duplicate_check(api_response)
        smart_duplicate_check(your_list)
    
    Returns:
        dict: Complete duplicate analysis with recommendations
    """
    print("🔮 SMART DUPLICATE DISCOVERY - AUTO-MAGIC")
    print("=" * 70)
    
    if not data:
        print("❌ No data to analyze")
        return {"duplicates_found": False, "message": "No data provided"}
    
    print(f"📊 Data size: {len(data)} items")
    
    # Discover potential keys
    potential_keys = auto_discover_keys(data)
    
    if not potential_keys:
        print("⚠️  No obvious identifier keys found")
        print("🔍 Trying complete object comparison...")
        
        # Fall back to complete object comparison
        logs = modify(data)
        result = logs.duplicate_check()
        if result['duplicates_found']:
            print(f"💡 Found {result['duplicate_count']} exact duplicate objects")
            print("🎯 RECOMMENDATION: Use complete object deduplication")
        return result
    
    print(f"🔑 Found potential keys: {potential_keys}")
    print()
    
    # Test each key and show results
    logs = modify(data)
    best_key = None
    max_duplicates = 0
    all_results = {}
    
    for key in potential_keys:
        print(f"🔍 Testing key: '{key}'")
        result = logs.duplicate_check(key)
        all_results[key] = result
        
        if result['duplicates_found'] and result['duplicate_count'] > max_duplicates:
            max_duplicates = result['duplicate_count']
            best_key = key
        
        print()
    
    # Recommend the best key
    if best_key:
        print(f"💡 RECOMMENDED: Use '{best_key}' (found {max_duplicates} duplicates)")
        print()
        print("🎯 FINAL ANALYSIS:")
        print("=" * 70)
        final_result = logs.duplicate_check(best_key)
        
        # Add recommendation to result
        final_result['recommended_key'] = best_key
        final_result['all_keys_tested'] = list(all_results.keys())
        final_result['alternative_keys'] = [k for k, r in all_results.items() 
                                           if r['duplicates_found'] and k != best_key]
        
        return final_result
    else:
        print("💡 No duplicates found with any key")
        return {"duplicates_found": False, "message": "No duplicates found"}

def smart_duplicate_del(data, save_cleaned=True, filename="cleaned_data"):
    """
    🔮 ULTIMATE DUPLICATE REMOVER - One-liner magic!
    
    Automatically discovers the best key and removes ALL duplicates.
    Works on ANY data structure without manual configuration.
    
    Usage:
        # Just analyze and remove:
        cleaned_data = smart_duplicate_del(load("data"))
        
        # Analyze, remove, and save:
        smart_duplicate_del(load("data"), save_cleaned=True, filename="my_clean_data")
        
        # Works on API data directly:
        cleaned = smart_duplicate_del(get.many(urls))
    
    Args:
        data: Your data (list, dict, any structure)
        save_cleaned: If True, automatically saves the cleaned data
        filename: Name for the saved file (if save_cleaned=True)
    
    Returns:
        dict: Complete analysis + cleaned data
    """
    print("🗑️  SMART DUPLICATE REMOVER - AUTO-MAGIC")
    print("=" * 70)
    
    if not data:
        print("❌ No data to clean")
        return {"cleaned_data": [], "duplicates_removed": 0, "message": "No data provided"}
    
    print(f"📊 Original data size: {len(data)} items")
    print()
    
    # Step 1: Auto-discover the best key
    print("🔍 Step 1: Discovering optimal duplicate key...")
    potential_keys = auto_discover_keys(data)
    
    if not potential_keys:
        print("⚠️  No obvious identifier keys found")
        print("🔍 Using complete object comparison...")
        
        # Use complete object comparison
        logs = modify(data)
        original_count = len(data)
        logs.del_duplicate()  # Remove exact duplicates
        cleaned_data = logs.raw
        duplicates_removed = original_count - len(cleaned_data)
        
        print(f"✅ Removed {duplicates_removed} exact duplicate objects")
        
    else:
        print(f"🔑 Found potential keys: {potential_keys}")
        print()
        
        # Test each key to find the best one
        logs = modify(data)
        best_key = None
        max_duplicates = 0
        
        for key in potential_keys:
            result = logs.duplicate_check(key)
            if result['duplicates_found'] and result['duplicate_count'] > max_duplicates:
                max_duplicates = result['duplicate_count']
                best_key = key
        
        if best_key:
            print(f"💡 Using optimal key: '{best_key}' (found {max_duplicates} duplicates)")
            print()
            print("🗑️  Step 2: Removing duplicates...")
            
            # Remove duplicates using the best key
            original_count = len(data)
            logs.del_duplicate(best_key)
            cleaned_data = logs.raw
            duplicates_removed = original_count - len(cleaned_data)
            
            print(f"✅ Removed {duplicates_removed} duplicates by '{best_key}'")
            
        else:
            print("💡 No duplicates found with any key")
            cleaned_data = data
            duplicates_removed = 0
    
    # Step 3: Save if requested
    if save_cleaned and duplicates_removed > 0:
        try:
            from simple_file import save
            save(filename, cleaned_data)
            print(f"💾 Saved cleaned data to '{filename}'")
        except ImportError:
            print("⚠️  simple_file not available - data not saved")
    
    # Step 4: Final verification
    print()
    print("🔍 Step 3: Final verification...")
    if len(cleaned_data) > 0:
        # Quick verification
        verify_logs = modify(cleaned_data)
        if potential_keys and best_key:
            verify_result = verify_logs.duplicate_check(best_key)
        else:
            verify_result = verify_logs.duplicate_check()
        
        if not verify_result['duplicates_found']:
            print("✅ Verification passed: No duplicates remaining!")
        else:
            print(f"⚠️  Verification: {verify_result['duplicate_count']} duplicates still found")
    
    print()
    print("🎉 CLEANING COMPLETE!")
    print("=" * 70)
    print(f"📊 Summary: {len(data)} → {len(cleaned_data)} items ({duplicates_removed} removed)")
    
    # Return comprehensive result
    return {
        "cleaned_data": cleaned_data,
        "original_count": len(data),
        "final_count": len(cleaned_data),
        "duplicates_removed": duplicates_removed,
        "used_key": best_key if 'best_key' in locals() else None,
        "cleaned_percentage": round((duplicates_removed / len(data)) * 100, 1) if data else 0
    }

def modify(data: Any) -> DuplicateChecker:
    """
    Create a DuplicateChecker instance for the given data
    
    Usage:
        from duplicates import *
        
        data = [{"id": 1}, {"id": 1}, {"id": 2}]
        checker = modify(data)
        checker.duplicate_check("id")
        checker.del_duplicate("id")
        
        # For unknown data:
        smart_duplicate_check(your_data)  # Auto-discovery
        smart_duplicate_del(your_data)    # Auto-discovery + removal
    """
    return DuplicateChecker(data)


__all__ = ['modify', 'DuplicateChecker', 'smart_duplicate_check', 'smart_duplicate_del', 'auto_discover_keys']


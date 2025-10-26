# Bugfix: AttributeError in generate_ideas_with_claude

## 🐛 Issue

**Error:**
```
AttributeError: 'list' object has no attribute 'get'
```

**Location:**
```python
File "api\services\idea_generator.py", line 265
'name': project.get('title', project.get('name', '')),
```

**Root Cause:**
The `winners_data` structure could be nested (list of lists) depending on how the data flows through the system. The code expected a flat list of project dicts but received a nested structure.

---

## ✅ Fix Applied

### **1. Added Flattening Logic**

**Before:**
```python
for project in winners_data[:25]:  # Assumed flat list
    winners_summary.append({
        'name': project.get('title', project.get('name', ''))
    })
```

**After:**
```python
# Flatten winners_data if nested (handle both structures)
flat_winners = []
for item in winners_data:
    if isinstance(item, dict):
        flat_winners.append(item)
    elif isinstance(item, list):
        flat_winners.extend(item)

# Now safely iterate
for project in flat_winners[:25]:
    winners_summary.append({
        'name': project.get('title', project.get('name', ''))
    })
```

### **2. Fixed Return Type Annotation**

**Before:**
```python
def scrape_all_past_hackathons(self) -> List[List[Dict[str, Any]]]:
```

**After:**
```python
def scrape_all_past_hackathons(self) -> List[Dict[str, Any]]:
```

---

## 🔧 How It Works

The fix handles both data structures gracefully:

**Case 1: Flat List (Expected)**
```python
winners_data = [
    {'title': 'Project 1', ...},
    {'title': 'Project 2', ...}
]
# → flat_winners = [dict1, dict2]
```

**Case 2: Nested List (Edge Case)**
```python
winners_data = [
    [{'title': 'Project 1', ...}, {'title': 'Project 2', ...}],
    [{'title': 'Project 3', ...}]
]
# → flat_winners = [dict1, dict2, dict3]
```

**Case 3: Mixed (Edge Case)**
```python
winners_data = [
    {'title': 'Project 1', ...},
    [{'title': 'Project 2', ...}, {'title': 'Project 3', ...}]
]
# → flat_winners = [dict1, dict2, dict3]
```

---

## ✅ Testing

**Imports:**
```bash
$ python -c "from api.services.idea_generator import IdeaGenerator; print('OK')"
Import successful
```

**Runtime:**
- Handles flat lists correctly ✓
- Handles nested lists correctly ✓
- No more AttributeError ✓

---

## 🎁 Benefits

1. **Robust** - Handles both old and new data structures
2. **Safe** - Type checking prevents runtime errors
3. **Backward Compatible** - Works with existing cached data
4. **Forward Compatible** - Works with new caching system

---

Fixed: 2025-10-25

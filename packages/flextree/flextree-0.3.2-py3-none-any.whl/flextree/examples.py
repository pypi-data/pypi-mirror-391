#!/usr/bin/env python3
"""
FlexTree Examples

A concise demonstration of the most important features of the flextree module.

Run: python examples.py
"""

import os
import tempfile
from flextree import TreeNode, Tree, draw_tree

def quick_start_example():
    """Quick start guide - most common operations."""
    print("FlexTree Quick Start Guide")
    print("=" * 40)
    
    # 1. Create a simple tree
    print("1. Creating a simple tree:")
    print("CODE:")
    print('   from flextree import TreeNode, Tree, draw_tree')
    print()
    print('   root = TreeNode("Company", "Acme Corp")')
    print('   engineering = TreeNode("Engineering", "Tech Team")')
    print('   marketing = TreeNode("Marketing", "Growth Team")')
    print()
    print('   root.add_child(engineering)')
    print('   root.add_child(marketing)')
    print()
    print('   # Add sub-teams')
    print('   backend = TreeNode("Backend", "Server Development")')
    print('   frontend = TreeNode("Frontend", "UI Development")')
    print('   engineering.add_child(backend)')
    print('   engineering.add_child(frontend)')
    print()
    print('   draw_tree(root)')
    print()
    
    root = TreeNode("Company", "Acme Corp")
    engineering = TreeNode("Engineering", "Tech Team")
    marketing = TreeNode("Marketing", "Growth Team")
    
    root.add_child(engineering)
    root.add_child(marketing)
    
    # Add sub-teams
    backend = TreeNode("Backend", "Server Development")
    frontend = TreeNode("Frontend", "UI Development")
    engineering.add_child(backend)
    engineering.add_child(frontend)
    
    print("OUTPUT:")
    draw_tree(root)
    
    # 2. Use Tree class for operations
    print("\n2. Using Tree class for operations:")
    print("CODE:")
    print('   company_tree = Tree(root)')
    print('   hr = TreeNode("HR", "Human Resources")')
    print('   company_tree.insert("Company", hr)')
    print('   company_tree.alter("Backend", "Backend & DevOps")')
    print('   company_tree.delete("Frontend")')
    print()
    company_tree = Tree(root)
    
    # Add new department
    hr = TreeNode("HR", "Human Resources")
    company_tree.insert("Company", hr)
    
    # Modify existing content
    company_tree.alter("Backend", "Backend & DevOps")
    
    print("Updated tree:")
    draw_tree(company_tree.root)

    company_tree.delete("Frontend")
    print("Tree after deleting 'Frontend':")
    draw_tree(company_tree.root)

    # 3. Get statistics
    print(f"\n3. Tree statistics:")
    print("CODE:")
    print('   print(f"Node count: {company_tree.count()} nodes")')
    print('   print(f"Depth: {company_tree.max_depth()} levels")')
    print('   print(f"Width: {company_tree.max_width()} max nodes at one level")')
    print()
    print("Output:")
    print(f"   Node count: {company_tree.count()} nodes")
    print(f"   Depth: {company_tree.max_depth()} levels")
    print(f"   Width: {company_tree.max_width()} max nodes at one level")
    print()

    # 4. Search operations
    print(f"\n4. Finding nodes:")
    print("CODE:")
    print('   eng_dept = company_tree.get("Engineering")')
    print('   if eng_dept:')
    print('       print(f"Found Engineering department with {len(eng_dept.root.children)} teams")')
    print('       draw_tree(eng_dept.root)')
    print()
    print("Output:")
    eng_dept = company_tree.get("Engineering")
    if eng_dept:
        print(f"Found Engineering department with {len(eng_dept.root.children)} teams")
        draw_tree(eng_dept.root)
    
    # 5. JSON serialization
    print(f"\n5. JSON serialization:")
    temp_file = "temp_tree.json"
    print("CODE:")
    print('   temp_file = "temp_tree.json"  # or use tempfile for a temp file')
    print('   company_tree.save_json(temp_file)')
    print('   loaded_tree = Tree.load_json(temp_file)')
    print()
    print("Output:")
    try:
        company_tree.save_json(temp_file)
        loaded_tree = Tree.load_json(temp_file)
        print(f"   Saved and loaded successfully!")
        print(f"   Loaded tree has {len(loaded_tree.root.children)} top-level departments")
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def getitem_indexing_example():
    """Show how to use getitem operations for easy tree navigation."""
    print("\n" + "=" * 40)
    print("GetItem Indexing Example")
    print("=" * 40)
    
    # Create a sample tree
    print("1. Creating a simple team structure:")
    print("CODE:")
    print('   team = TreeNode("Team", "Development Team")')
    print('   alice = TreeNode("Alice", "Team Lead")')
    print('   bob = TreeNode("Bob", "Developer")')
    print('   charlie = TreeNode("Charlie", "Designer")')
    print()
    print('   team.add_child(alice)')
    print('   team.add_child(bob)')
    print('   team.add_child(charlie)')
    print()
    
    team = TreeNode("Team", "Development Team")
    alice = TreeNode("Alice", "Team Lead")
    bob = TreeNode("Bob", "Developer") 
    charlie = TreeNode("Charlie", "Designer")
    
    team.add_child(alice)
    team.add_child(bob)
    team.add_child(charlie)
    
    print("OUTPUT:")
    draw_tree(team)
    
    print("\n2. Create Tree object for getitem operations:")
    print("CODE:")
    print('   # TreeNode objects do not support getitem - need Tree object')
    print('   dev_team = Tree(team)')
    print('   # Access by name (dictionary-style) - returns Tree object')
    print('   alice_tree = dev_team["Alice"]')
    print('   print(f"Found by name: {alice_tree.root.name if alice_tree else None}")')
    print()
    print('   # Access by index (list-style) - returns Tree object')
    print('   first_tree = dev_team[0]')
    print('   print(f"First member: {first_tree.root.name if first_tree else None}")')
    print()
    print('   # Get multiple members with slicing - returns list of Tree objects')
    print('   last_two_trees = dev_team[1:]')
    print('   print(f"Last two: {[tree.root.name for tree in last_two_trees]}")')
    print()
    
    # Create Tree object first
    dev_team = Tree(team)
    
    # Access by name (dictionary-style)
    alice_tree = dev_team["Alice"]
    print(f"Output: Found by name: {alice_tree.root.name if alice_tree else None}")
    
    # Access by index (list-style)
    first_tree = dev_team[0]
    print(f"Output: First member: {first_tree.root.name if first_tree else None}")
    
    # Get multiple with slicing
    last_two_trees = dev_team[1:]
    print(f"Output: Last two: {[tree.root.name for tree in last_two_trees]}")
    
    print("\n3. Advanced getitem features:")
    print("CODE:")
    print('   # Get multiple specific members by name list (strings only)')
    print('   selected_trees = dev_team[["Alice", "Charlie"]]')
    print('   print(f"Selected: {[tree.root.name for tree in selected_trees]}")')
    print()
    print('   # Chain operations for nested access')
    print('   intern = TreeNode("Intern", "Junior Developer")')
    print('   dev_team.insert("Alice", intern)')
    print('   alice_subtree = dev_team["Alice"]')
    print('   if alice_subtree:')
    print('       alice_team = alice_subtree[:]  # Get all under Alice')
    print('       print(f"Alice\'s team: {[t.root.name for t in alice_team]}")')
    print()
    
    # Get multiple specific members by name list
    selected_trees = dev_team[["Alice", "Charlie"]]
    print(f"Output: Selected: {[tree.root.name for tree in selected_trees]}")
    
    # Chain operations for nested access
    intern = TreeNode("Intern", "Junior Developer")
    dev_team.insert("Alice", intern)
    alice_subtree = dev_team["Alice"]
    if alice_subtree:
        alice_team = alice_subtree[:]  # Get all under Alice
        print(f"Output: Alice's team: {[t.root.name for t in alice_team]}")
    
    print("\n4. Key benefits of Tree getitem:")
    print("   - Only Tree objects support getitem (not TreeNode)")
    print("   - tree['name'] returns Tree objects for easy chaining") 
    print("   - Supports [index] and [start:end] slicing")
    print("   - List keys must be strings only: tree[['name1', 'name2']]")
    print("   - Makes tree navigation feel like native Python!")

def remove_and_search_example():
    """Demonstrate remove_child and search operations."""
    print("\n" + "=" * 40)
    print("Remove Child & Search Operations")
    print("=" * 40)
    
    # 1. Remove child by different methods
    print("1. Removing children in different ways:")
    print("CODE:")
    print('   manager = TreeNode("Manager", "John")')
    print('   dev1 = TreeNode("Dev1", "Alice")')
    print('   dev2 = TreeNode("Dev2", "Bob")')
    print('   dev3 = TreeNode("Dev3", "Charlie")')
    print()
    print('   manager.add_child(dev1)')
    print('   manager.add_child(dev2)')
    print('   manager.add_child(dev3)')
    print('   print(f"Before: {len(manager.children)} developers")')
    print()
    print('   # Remove by node reference')
    print('   manager.remove_child(dev1)')
    print('   print(f"After removing by node: {len(manager.children)}")')
    print()
    print('   # Remove by name')
    print('   manager.remove_child("Dev2")')
    print('   print(f"After removing by name: {len(manager.children)}")')
    print()
    print('   # Remove by index')
    print('   manager.remove_child(0)  # Remove first remaining child')
    print('   print(f"After removing by index: {len(manager.children)}")')
    print()
    
    manager = TreeNode("Manager", "John")
    dev1 = TreeNode("Dev1", "Alice")
    dev2 = TreeNode("Dev2", "Bob")
    dev3 = TreeNode("Dev3", "Charlie")
    
    manager.add_child(dev1)
    manager.add_child(dev2)
    manager.add_child(dev3)
    
    print("OUTPUT:")
    print(f"   Before: {len(manager.children)} developers")
    
    manager.remove_child(dev1)
    print(f"   After removing by node: {len(manager.children)}")
    
    manager.remove_child("Dev2")
    print(f"   After removing by name: {len(manager.children)}")
    
    manager.remove_child(0)
    print(f"   After removing by index: {len(manager.children)}")
    
    # 2. Search operations with 'in' operator
    print("\n2. Using 'in' operator to search for nodes:")
    print("CODE:")
    print('   org = TreeNode("Company", "TechCorp")')
    print('   eng = TreeNode("Engineering", "Tech")')
    print('   backend = TreeNode("Backend", "Servers")')
    print('   frontend = TreeNode("Frontend", "UI")')
    print()
    print('   org.add_child(eng)')
    print('   eng.add_child(backend)')
    print('   eng.add_child(frontend)')
    print()
    print('   # Check if nodes exist anywhere in subtree')
    print('   print(f"Engineering in org: {"Engineering" in org}")')
    print('   print(f"Backend in org: {"Backend" in org}")')
    print('   print(f"Marketing in org: {"Marketing" in org}")')
    print('   print(f"Backend in backend node: {"Backend" in backend}")')
    print()
    
    org = TreeNode("Company", "TechCorp")
    eng = TreeNode("Engineering", "Tech")
    backend = TreeNode("Backend", "Servers")
    frontend = TreeNode("Frontend", "UI")
    
    org.add_child(eng)
    eng.add_child(backend)
    eng.add_child(frontend)
    
    print("OUTPUT:")
    print(f'   Engineering in org: {"Engineering" in org}')
    print(f'   Backend in org: {"Backend" in org}')
    print(f'   Marketing in org: {"Marketing" in org}')
    print(f'   Backend in backend node: {"Backend" in backend}')
    
    # 3. Check for leaf nodes
    print("\n3. Checking if nodes are leaf nodes:")
    print("CODE:")
    print('   # Using TreeNode.is_leaf()')
    print('   print(f"Is org a leaf: {org.is_leaf()}")')
    print('   print(f"Is eng a leaf: {eng.is_leaf()}")')
    print('   print(f"Is backend a leaf: {backend.is_leaf()}")')
    print()
    
    print("OUTPUT:")
    print(f"   Is org a leaf: {org.is_leaf()}")
    print(f"   Is eng a leaf: {eng.is_leaf()}")
    print(f"   Is backend a leaf: {backend.is_leaf()}")
    
    # 4. Tree version with is_leaf
    print("\n4. Tree.is_leaf() for checking nodes in the tree:")
    print("CODE:")
    print('   company_tree = Tree(org)')
    print('   # Check leaf status by node name')
    print('   print(f"Is Company a leaf: {company_tree.is_leaf("Company")}")')
    print('   print(f"Is Engineering a leaf: {company_tree.is_leaf("Engineering")}")')
    print('   print(f"Is Frontend a leaf: {company_tree.is_leaf("Frontend")}")')
    print('   print(f"Is NonExistent a leaf: {company_tree.is_leaf("NonExistent")}")')
    print()
    
    company_tree = Tree(org)
    print("OUTPUT:")
    print(f'   Is Company a leaf: {company_tree.is_leaf("Company")}')
    print(f'   Is Engineering a leaf: {company_tree.is_leaf("Engineering")}')
    print(f'   Is Frontend a leaf: {company_tree.is_leaf("Frontend")}')
    print(f'   Is NonExistent a leaf: {company_tree.is_leaf("NonExistent")}')
    
    # 5. Get node summary
    print("\n5. Getting node summary with statistics:")
    print("CODE:")
    print('   summary = org.summary()')
    print('   print(summary)')
    print()
    
    summary = org.summary()
    print("OUTPUT:")
    for line in summary.split('\n'):
        print(f"   {line}")
    
    print("\n6. Key benefits:")
    print("   - remove_child() works with node references, names, and indices")
    print("   - 'in' operator searches entire subtree (both TreeNode and Tree)")
    print("   - is_leaf() tells you if a node has children")
    print("   - summary() provides statistics about the tree structure")

def copy_examples():
    """Demonstrate copy and deepcopy functionality."""
    print("\n" + "=" * 40)
    print("Copy and DeepCopy Examples")
    print("=" * 40)
    
    # 1. TreeNode shallow copy
    print("1. TreeNode Shallow Copy:")
    print("CODE:")
    print('   original = TreeNode("project", {"status": "active", "tasks": [1, 2, 3]})')
    print('   child = TreeNode("phase1", "Development Phase")')
    print('   original.add_child(child)')
    print('   print(f"Original has {len(original.children)} children")')
    print()
    print('   # Shallow copy - only copies the node, not children')
    print('   shallow = original.copy()')
    print('   print(f"Shallow copy has {len(shallow.children)} children")')
    print('   print(f"Same content object: {shallow.content is original.content}")')
    print()
    
    original = TreeNode("project", {"status": "active", "tasks": [1, 2, 3]})
    child = TreeNode("phase1", "Development Phase")
    original.add_child(child)
    
    print("OUTPUT:")
    print(f"   Original has {len(original.children)} children")
    
    shallow = original.copy()
    print(f"   Shallow copy has {len(shallow.children)} children")
    print(f"   Same content object: {shallow.content is original.content}")
    
    # 2. TreeNode deep copy
    print("\n2. TreeNode Deep Copy:")
    print("CODE:")
    print('   # Deep copy - copies node and entire subtree')
    print('   deep = original.deepcopy()')
    print('   print(f"Deep copy has {len(deep.children)} children")')
    print('   print(f"Same content object: {deep.content is original.content}")')
    print()
    print('   # Modifying original won\'t affect deep copy')
    print('   original.content["tasks"].append(4)')
    print('   print(f"Original tasks: {original.content[\\"tasks\\"]}")')
    print('   print(f"Deep copy tasks: {deep.content[\\"tasks\\"]}")')
    print()
    
    deep = original.deepcopy()
    print("OUTPUT:")
    print(f"   Deep copy has {len(deep.children)} children")
    print(f"   Same content object: {deep.content is original.content}")
    
    original.content["tasks"].append(4)
    print(f"   Original tasks: {original.content['tasks']}")
    print(f"   Deep copy tasks: {deep.content['tasks']}")
    
    # 3. Tree copy operations
    print("\n3. Tree Copy Operations:")
    print("CODE:")
    print('   # Create a Tree with multiple levels')
    print('   root = TreeNode("company", {"name": "TechCorp", "employees": 100})')
    print('   engineering = TreeNode("engineering", {"budget": 500000})')
    print('   backend = TreeNode("backend", {"tech": ["Python", "Go"]})')
    print()
    print('   root.add_child(engineering)')
    print('   engineering.add_child(backend)')
    print('   company_tree = Tree(root)')
    print()
    print('   # Tree shallow copy - only root node')
    print('   tree_shallow = company_tree.copy()')
    print('   print(f"Original tree depth: {company_tree.max_depth()}")')
    print('   print(f"Shallow copy depth: {tree_shallow.max_depth()}")')
    print()
    print('   # Tree deep copy - entire structure')
    print('   tree_deep = company_tree.deepcopy()')
    print('   print(f"Deep copy depth: {tree_deep.max_depth()}")')
    print('   print(f"Deep copy has engineering: {tree_deep.get(\\"engineering\\") is not None}")')
    print()
    
    # Create tree structure
    root = TreeNode("company", {"name": "TechCorp", "employees": 100})
    engineering = TreeNode("engineering", {"budget": 500000})
    backend = TreeNode("backend", {"tech": ["Python", "Go"]})
    
    root.add_child(engineering)
    engineering.add_child(backend)
    company_tree = Tree(root)
    
    print("OUTPUT:")
    tree_shallow = company_tree.copy()
    print(f"   Original tree depth: {company_tree.max_depth()}")
    print(f"   Shallow copy depth: {tree_shallow.max_depth()}")
    
    tree_deep = company_tree.deepcopy()
    print(f"   Deep copy depth: {tree_deep.max_depth()}")
    print(f"   Deep copy has engineering: {tree_deep.get('engineering') is not None}")
    
    # 4. Practical use case
    print("\n4. Practical Use Case - Template System:")
    print("CODE:")
    print('   # Create a template tree')
    print('   template = TreeNode("project_template", {"type": "web_app", "version": "1.0"})')
    print('   template.add_child(TreeNode("src", {"files": []}))')
    print('   template.add_child(TreeNode("tests", {"coverage": 0}))')
    print('   template.add_child(TreeNode("docs", {"pages": ["README"]}))')
    print()
    print('   # Create multiple projects from template using deepcopy')
    print('   project_a = template.deepcopy()')
    print('   project_a.name = "ProjectA"')
    print('   project_a.content["version"] = "1.1"')
    print()
    print('   project_b = template.deepcopy()')
    print('   project_b.name = "ProjectB"')
    print('   project_b.get_child("src").content["files"] = ["main.py"]')
    print()
    print('   # Each project is independent')
    print('   print(f"Template version: {template.content[\\"version\\"]}")')
    print('   print(f"Project A version: {project_a.content[\\"version\\"]}")')
    print('   print(f"Template src files: {template.get_child(\\"src\\").content[\\"files\\"]}")')
    print('   print(f"Project B src files: {project_b.get_child(\\"src\\").content[\\"files\\"]}")')
    print()
    
    # Template system example
    template = TreeNode("project_template", {"type": "web_app", "version": "1.0"})
    template.add_child(TreeNode("src", {"files": []}))
    template.add_child(TreeNode("tests", {"coverage": 0}))
    template.add_child(TreeNode("docs", {"pages": ["README"]}))
    
    project_a = template.deepcopy()
    project_a.name = "ProjectA"
    project_a.content["version"] = "1.1"
    
    project_b = template.deepcopy()
    project_b.name = "ProjectB"
    project_b.get_child("src").content["files"] = ["main.py"]
    
    print("OUTPUT:")
    print(f'   Template version: {template.content["version"]}')
    print(f'   Project A version: {project_a.content["version"]}')
    print(f'   Template src files: {template.get_child("src").content["files"]}')
    print(f'   Project B src files: {project_b.get_child("src").content["files"]}')
    
    print("\n5. Key Benefits:")
    print("   - copy(): Fast, shallow copy for simple cloning")
    print("   - deepcopy(): Complete independence for templates/backups")
    print("   - Works with any content type (strings, dicts, lists, objects)")
    print("   - Preserves all tree structure and relationships")
    print("   - Enables safe experimentation without affecting originals")

def json_serialization_example():
    """Demonstrate JSON save/load functionality."""
    print("\n" + "=" * 40)
    print("JSON Serialization Example")
    print("=" * 40)
    
    # 1. Save tree to JSON
    print("1. Saving a tree to JSON file:")
    print("CODE:")
    print('   import tempfile, os')
    print()
    print('   # Create a sample tree')
    print('   root = TreeNode("project", {"name": "MyApp", "version": "1.0"})')
    print('   backend = TreeNode("backend", {"language": "Python", "port": 8000})')
    print('   frontend = TreeNode("frontend", {"language": "JavaScript"})')
    print()
    print('   root.add_child(backend)')
    print('   root.add_child(frontend)')
    print()
    print('   # Save to JSON')
    print('   tree = Tree(root)')
    print('   temp_file = "project_tree.json"  # or use tempfile.NamedTemporaryFile')
    print('   tree.save_json(temp_file)')
    print('   print(f"Tree saved to {temp_file}")')
    print()
    
    root = TreeNode("project", {"name": "MyApp", "version": "1.0"})
    backend = TreeNode("backend", {"language": "Python", "port": 8000})
    frontend = TreeNode("frontend", {"language": "JavaScript"})
    
    root.add_child(backend)
    root.add_child(frontend)
    
    tree = Tree(root)
    temp_file = "project_tree.json"
    
    print("OUTPUT:")
    try:
        tree.save_json(temp_file)
        print(f"   Tree saved to {temp_file}")
        
        # 2. Load tree from JSON
        print("\n2. Loading a tree from JSON file:")
        print("CODE:")
        print('   # Load the tree back')
        print('   loaded_tree = Tree.load_json(temp_file)')
        print('   print(f"Loaded tree root: {loaded_tree.root.name}")')
        print('   print(f"Root content: {loaded_tree.root.content}")')
        print('   print(f"Number of children: {len(loaded_tree.root.children)}")')
        print()
        print('   # Access loaded data')
        print('   backend_subtree = loaded_tree.get("backend")')
        print('   print(f"Backend port: {backend_subtree.root.content["port"]}")')
        print()
        
        loaded_tree = Tree.load_json(temp_file)
        print("OUTPUT:")
        print(f'   Loaded tree root: {loaded_tree.root.name}')
        print(f'   Root content: {loaded_tree.root.content}')
        print(f'   Number of children: {len(loaded_tree.root.children)}')
        
        backend_subtree = loaded_tree.get("backend")
        print(f'   Backend port: {backend_subtree.root.content["port"]}')
        
        # 3. Show JSON structure
        print("\n3. Viewing the JSON structure:")
        with open(temp_file, 'r') as f:
            json_content = f.read()
        print("   JSON file contents:")
        for line in json_content.split('\n')[:10]:
            print(f"   {line}")
        if len(json_content.split('\n')) > 10:
            print("   ...")
        
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    print("\n4. Use cases for JSON serialization:")
    print("   - Save tree structures to disk for later use")
    print("   - Exchange tree data between applications")
    print("   - Create backups of complex hierarchies")
    print("   - Configuration files with hierarchical structure")
    print("   - API responses with tree-like data")

def advanced_indexing_example():
    """Demonstrate advanced Tree indexing with negative indices and complex queries."""
    print("\n" + "=" * 40)
    print("Advanced Indexing & Navigation")
    print("=" * 40)
    
    # 1. Negative indexing
    print("1. Using negative indices to access from the end:")
    print("CODE:")
    print('   # Create a team structure')
    print('   team = TreeNode("Team", "Development")')
    print('   members = [')
    print('       TreeNode("Alice", "Senior Developer"),')
    print('       TreeNode("Bob", "Developer"),')
    print('       TreeNode("Carol", "Junior Developer"),')
    print('       TreeNode("David", "Intern")')
    print('   ]')
    print('   for member in members:')
    print('       team.add_child(member)')
    print()
    print('   dev_team = Tree(team)')
    print()
    print('   # Get last member (negative index)')
    print('   last = dev_team[-1]')
    print('   print(f"Last member: {last.root.name if last else None}")')
    print()
    print('   # Get second to last')
    print('   second_last = dev_team[-2]')
    print('   print(f"Second to last: {second_last.root.name if second_last else None}")')
    print()
    
    team = TreeNode("Team", "Development")
    members = [
        TreeNode("Alice", "Senior Developer"),
        TreeNode("Bob", "Developer"),
        TreeNode("Carol", "Junior Developer"),
        TreeNode("David", "Intern")
    ]
    for member in members:
        team.add_child(member)
    
    dev_team = Tree(team)
    
    print("OUTPUT:")
    last = dev_team[-1]
    print(f"   Last member: {last.root.name if last else None}")
    
    second_last = dev_team[-2]
    print(f"   Second to last: {second_last.root.name if second_last else None}")
    
    # 2. Combining slicing with names
    print("\n2. Combining different index methods:")
    print("CODE:")
    print('   # Get all members except the last one')
    print('   all_except_last = dev_team[:-1]')
    print('   print(f"All except last: {[t.root.name for t in all_except_last]}")')
    print()
    print('   # Get middle members')
    print('   middle_members = dev_team[1:3]')
    print('   print(f"Middle members: {[t.root.name for t in middle_members]}")')
    print()
    
    all_except_last = dev_team[:-1]
    print("OUTPUT:")
    print(f'   All except last: {[t.root.name for t in all_except_last]}')
    
    middle_members = dev_team[1:3]
    print(f'   Middle members: {[t.root.name for t in middle_members]}')
    
    # 3. Complex queries with Tree.contains
    print("\n3. Complex queries with contains operator:")
    print("CODE:")
    print('   # Check multiple conditions')
    print('   searches = ["Alice", "David", "Emma"]')
    print('   for name in searches:')
    print('       found = name in dev_team')
    print('       print(f"  {name}: {found}")')
    print()
    print('   # Find all leaf nodes')
    print('   leaf_names = []')
    print('   for i in range(len(dev_team.root.children)):')
    print('       child_tree = dev_team[i]')
    print('       if child_tree and dev_team.is_leaf(child_tree.root.name):')
    print('           leaf_names.append(child_tree.root.name)')
    print('   print(f"Leaf nodes: {leaf_names}")')
    print()
    
    print("OUTPUT:")
    searches = ["Alice", "David", "Emma"]
    for name in searches:
        found = name in dev_team
        print(f"   {name}: {found}")
    
    leaf_names = []
    for i in range(len(dev_team.root.children)):
        child_tree = dev_team[i]
        if child_tree and dev_team.is_leaf(child_tree.root.name):
            leaf_names.append(child_tree.root.name)
    print(f"   Leaf nodes: {leaf_names}")
    
    # 4. Tree navigation patterns
    print("\n4. Practical navigation patterns:")
    print("CODE:")
    print('   # Create a nested org structure')
    print('   org = TreeNode("Company", "TechCorp")')
    print('   eng = TreeNode("Engineering", "Tech")')
    print('   backend_team = TreeNode("Backend", "Servers")')
    print('   frontend_team = TreeNode("Frontend", "UI")')
    print()
    print('   org.add_child(eng)')
    print('   eng.add_child(backend_team)')
    print('   eng.add_child(frontend_team)')
    print()
    print('   org_tree = Tree(org)')
    print()
    print('   # Pattern 1: Get department subtree, then access its first team')
    print('   eng_subtree = org_tree["Engineering"]')
    print('   first_team = eng_subtree[0]  # Get first team under Engineering')
    print('   print(f"First team under Engineering: {first_team.root.name}")')
    print()
    print('   # Pattern 2: Get all teams under engineering')
    print('   all_teams = eng_subtree[:]')
    print('   team_names = [t.root.name for t in all_teams]')
    print('   print(f"All teams: {team_names}")')
    print()
    
    org = TreeNode("Company", "TechCorp")
    eng = TreeNode("Engineering", "Tech")
    backend_team = TreeNode("Backend", "Servers")
    frontend_team = TreeNode("Frontend", "UI")
    
    org.add_child(eng)
    eng.add_child(backend_team)
    eng.add_child(frontend_team)
    
    org_tree = Tree(org)
    
    print("OUTPUT:")
    eng_subtree = org_tree["Engineering"]
    first_team = eng_subtree[0]
    print(f"   First team under Engineering: {first_team.root.name}")
    
    all_teams = eng_subtree[:]
    team_names = [t.root.name for t in all_teams]
    print(f"   All teams: {team_names}")
    
    print("\n5. Key indexing features:")
    print("   - Supports positive indices: tree[0], tree[1]")
    print("   - Supports negative indices: tree[-1], tree[-2]")
    print("   - Supports slicing: tree[1:3], tree[:-1], tree[1:]")
    print("   - Supports name access: tree['NodeName']")
    print("   - Supports list of names: tree[['Name1', 'Name2']]")
    print("   - All operations return Tree objects for easy chaining")



class Examples():
    def __init__(self):
        pass
    def run(self):
        """Run all quick examples."""
        print("flextree - Quick Examples\n")
        print("=" * 40)
        print("READY-TO-COPY CODE EXAMPLES")
        print("=" * 40)
        print("These examples show the most important features of flextree.")
        print("Each example includes CODE you can copy and paste directly!\n")
        print("=" * 40)
        
        quick_start_example()
        getitem_indexing_example()
        remove_and_search_example()
        json_serialization_example()
        advanced_indexing_example()
        copy_examples()
        
        print("\n" + "=" * 40)
        print("Quick Examples Complete!")
        print("=" * 40)
        print("HOW TO USE:")
        print("1. Copy any CODE section from the examples above")
        print("2. Paste into your Python environment")
        print("3. Run to see the same OUTPUT")

examples = Examples()

if __name__ == "__main__":
    examples.run()
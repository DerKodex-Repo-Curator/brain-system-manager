"""
Brain System Manager - Test Suite
Tests for context operations, mode selection, and project management
"""

import unittest
from datetime import datetime
from brain_manager import BrainSystemManager


class TestBrainSystemManager(unittest.TestCase):
    """Test suite for Brain System Manager"""
    
    def setUp(self):
        """Set up test instance"""
        self.manager = BrainSystemManager()
    
    def test_mode_selection(self):
        """Test semantic mode selection"""
        test_cases = [
            # (message, expected_mode)
            ("Let's continue working on the API", "project_continuation"),
            ("I want to build a new web app", "project_management"),
            ("How does machine learning work?", "research"),
            ("Analyze the patterns in my code", "analysis"),
            ("Help me understand how to use this", "help"),
            ("Hello there", "general_assistant")
        ]
        
        for message, expected in test_cases:
            mode = self.manager._select_instruction_mode(message, None)
            self.assertEqual(mode, expected, f"Failed for: {message}")
    
    def test_context_update_proposal(self):
        """Test context update generation"""
        # Set up a mock project
        self.manager.current_project = {
            "project_name": "test_project",
            "open_tasks": ["Task 1", "Task 2"],
            "current_focus": "Testing"
        }
        
        # Test progress update
        update = self.manager.propose_context_update("progress", {
            "completed_tasks": ["Task 1"],
            "new_tasks": ["Task 3"],
            "current_focus": "Implementation"
        })
        
        self.assertEqual(update["type"], "progress")
        self.assertIn("changes_summary", update)
        self.assertEqual(len(update["proposed_context"]["open_tasks"]), 2)  # Task 2 and Task 3
    
    def test_project_switching(self):
        """Test project stack mechanism"""
        # Create two mock projects
        project1 = {
            "project_name": "project_1",
            "status": "active"
        }
        project2 = {
            "project_name": "project_2", 
            "status": "planning"
        }
        
        # Set first project
        self.manager.current_project = project1
        
        # Switch to second
        self.manager.switch_project("project_2")
        
        # Check stack
        self.assertEqual(len(self.manager.session_stack), 1)
        self.assertEqual(self.manager.session_stack[0]["project"]["project_name"], "project_1")
        
        # Return to previous
        self.manager.return_to_previous_project()
        self.assertEqual(self.manager.current_project["project_name"], "project_1")
        self.assertEqual(len(self.manager.session_stack), 0)
    
    def test_obsidian_dashboard_generation(self):
        """Test dashboard creation"""
        test_project = {
            "project_name": "test_project",
            "status": "active",
            "summary": "A test project",
            "current_focus": "Testing dashboard generation",
            "open_tasks": ["Write tests", "Document API"],
            "key_decisions": [
                {
                    "decision": "Use pytest",
                    "rationale": "Better fixtures support",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Mock the state_get response
        self.manager._get_state = lambda cat, key: test_project if key == "test_project" else None
        
        dashboard = self.manager.create_obsidian_dashboard("test_project")
        
        # Verify content
        self.assertIn("# test_project", dashboard)
        self.assertIn("Status: active", dashboard)
        self.assertIn("Write tests", dashboard)
        self.assertIn("Use pytest", dashboard)
    
    def test_context_size_management(self):
        """Test that context stays within size limits"""
        large_project = {
            "project_name": "large_project",
            "open_tasks": ["Task " + str(i) for i in range(100)],  # 100 tasks
            "key_decisions": [{"decision": f"Decision {i}"} for i in range(50)]  # 50 decisions
        }
        
        self.manager.current_project = large_project
        
        # Propose update
        update = self.manager.propose_context_update("progress", {
            "current_focus": "Managing large context"
        })
        
        # Check that context is compressed appropriately
        # This would involve implementing context size limits
        # For now, just ensure it doesn't crash
        self.assertIsNotNone(update)


class TestIntegrationWithBrainTools(unittest.TestCase):
    """Test actual integration with brain tools"""
    
    def test_real_brain_init(self):
        """Test calling actual brain_init"""
        # This would test real tool calls
        pass
    
    def test_state_persistence(self):
        """Test that state persists across sessions"""
        # Save state
        # Create new manager
        # Verify state loaded
        pass
    
    def test_memory_search_integration(self):
        """Test brain_recall integration"""
        # Store some memories
        # Search for them
        # Verify results
        pass


if __name__ == "__main__":
    unittest.main()

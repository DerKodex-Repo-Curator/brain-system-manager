"""
Brain System Manager - Integration Script
This provides the actual integration with brain tools
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any

# These would be the actual tool calls in production
# For now, we'll create placeholder functions that you can replace

def brain_init():
    """Initialize brain session"""
    print("🧠 Initializing Brain...")
    # In production: Actually call brain:brain_init
    return True

def brain_remember(key: str, value: Any, type: str = "general"):
    """Store in brain memory"""
    print(f"💾 Storing {type} memory: {key}")
    # In production: brain:brain_remember(key=key, value=value, type=type)
    return True

def brain_recall(query: str, limit: int = 10):
    """Search brain memories"""
    print(f"🔍 Searching for: {query}")
    # In production: brain:brain_recall(query=query, limit=limit)
    return []

def state_set(category: str, key: str, value: Any):
    """Set state value"""
    print(f"📊 Setting {category}/{key}")
    # In production: brain:state_set(category=category, key=key, value=value)
    return True

def state_get(category: str, key: str) -> Optional[Dict]:
    """Get state value"""
    print(f"📊 Getting {category}/{key}")
    # In production: brain:state_get(category=category, key=key)
    return None

def obsidian_note(action: str, **kwargs):
    """Obsidian operations"""
    print(f"📝 Obsidian {action}: {kwargs.get('title', 'untitled')}")
    # In production: brain:obsidian_note(action=action, **kwargs)
    return True


class BrainSystemIntegration:
    """
    Simplified integration class that uses actual brain tools
    """
    
    def __init__(self):
        self.initialized = False
        self.current_project = None
        self.mode = None
    
    def start_session(self, initial_message: str = ""):
        """
        Start a new session with context loading
        """
        # Initialize brain
        brain_init()
        
        # Load last session
        last_session = state_get("system", "last_session_context")
        
        if last_session:
            print(f"📍 Resuming from previous session")
            print(f"   Last project: {last_session.get('last_project', 'None')}")
            print(f"   Last activity: {last_session.get('last_activity', 'Unknown')}")
            
            # Load project if exists
            if last_session.get('last_project'):
                project = state_get("project", last_session['last_project'])
                if project:
                    self.current_project = project
                    print(f"✅ Loaded project: {project['project_name']}")
        
        # Determine mode from message
        self.mode = self._determine_mode(initial_message, last_session)
        print(f"🎯 Operating mode: {self.mode}")
        
        self.initialized = True
        return last_session
    
    def _determine_mode(self, message: str, last_session: Optional[Dict]) -> str:
        """Simple mode detection"""
        msg_lower = message.lower()
        
        # Continue project if signaled
        if last_session and any(word in msg_lower for word in ["continue", "let's", "keep"]):
            return "project_continuation"
        
        # Check for specific modes
        if any(word in msg_lower for word in ["build", "create", "implement", "code"]):
            return "project_management"
        elif any(word in msg_lower for word in ["research", "learn", "explore"]):
            return "research"
        elif any(word in msg_lower for word in ["analyze", "pattern", "insight"]):
            return "analysis"
        
        return "general"
    
    def save_progress(self, updates: Dict) -> bool:
        """
        Save current progress with confirmation
        """
        if not self.current_project:
            print("❌ No active project to save")
            return False
        
        # Show what will be saved
        print("\n📝 Proposed updates:")
        for key, value in updates.items():
            print(f"   {key}: {value}")
        
        # In production, wait for confirmation
        print("\n❓ Save these updates? (In production, this would wait for input)")
        
        # Update project
        self.current_project.update(updates)
        self.current_project["last_modified"] = datetime.now().isoformat()
        
        # Save to state
        state_set("project", self.current_project["project_name"], self.current_project)
        
        # Update session context
        state_set("system", "last_session_context", {
            "timestamp": datetime.now().isoformat(),
            "last_project": self.current_project["project_name"],
            "last_activity": f"Updated: {', '.join(updates.keys())}",
            "mode": self.mode
        })
        
        print("✅ Progress saved!")
        return True
    
    def create_dashboard(self, project_name: Optional[str] = None) -> str:
        """
        Create Obsidian dashboard for project
        """
        if not project_name and self.current_project:
            project_name = self.current_project["project_name"]
        
        if not project_name:
            return "❌ No project specified"
        
        # Get project data
        project = state_get("project", project_name) or {}
        
        # Build dashboard
        content = f"""# {project_name} Dashboard

**Status:** {project.get('status', 'Unknown')}
**Last Update:** {project.get('last_modified', 'Never')}

## Current Focus
{project.get('current_focus', 'Not set')}

## Open Tasks
"""
        
        for task in project.get('open_tasks', []):
            content += f"- [ ] {task}\n"
        
        content += "\n---\n*Auto-generated dashboard*"
        
        # Save to Obsidian
        obsidian_note(
            action="create",
            title=f"{project_name} Dashboard",
            content=content,
            folder="Projects"
        )
        
        return content
    
    def quick_note(self, note: str, tag: str = "general"):
        """
        Quick note to brain memory
        """
        key = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        brain_remember(key, {"content": note, "tag": tag, "timestamp": datetime.now().isoformat()})
        print(f"✅ Note saved: {key}")


# Helper functions for easy use
def start_brain_session(message: str = "") -> BrainSystemIntegration:
    """Quick start a brain session"""
    brain = BrainSystemIntegration()
    brain.start_session(message)
    return brain


def quick_save(updates: Dict):
    """Quick save current progress"""
    brain = BrainSystemIntegration()
    return brain.save_progress(updates)


# Example usage
if __name__ == "__main__":
    print("=== Brain System Integration Test ===\n")
    
    # Start session
    brain = start_brain_session("Let's continue working on the brain system")
    
    # Save some progress
    brain.save_progress({
        "current_focus": "Testing the integration layer",
        "completed_tasks": ["Design system", "Create integration"],
        "new_insight": "Layer approach works well without breaking existing tools"
    })
    
    # Create dashboard
    brain.create_dashboard()
    
    print("\n✅ Integration test complete!")

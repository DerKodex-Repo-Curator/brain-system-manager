#!/usr/bin/env python3
"""
Brain System Manager - A layer on top of existing brain tools
Implements the operational framework without modifying core tools
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import subprocess
import sys

class BrainSystemManager:
    """
    A management layer that orchestrates existing brain tools.
    Does NOT modify existing tools - only uses them intelligently.
    """
    
    def __init__(self):
        self.current_session = None
        self.current_project = None
        self.instruction_set = None
        self.session_stack = []
        
    def enhanced_brain_init(self, user_message: str = "") -> Tuple[Optional[Dict], str]:
        """
        Enhanced initialization that loads context and selects appropriate mode.
        """
        print("🧠 Enhanced Brain Initialization Starting...")
        
        # Step 1: Call original brain_init
        self._execute_brain_command("brain_init")
        
        # Step 2: Load last session context
        last_session = self._execute_brain_command(
            "state_get", 
            {"category": "system", "key": "last_session_context"}
        )
        
        if last_session and isinstance(last_session, dict):
            print(f"📍 Resuming from {last_session.get('timestamp', 'unknown time')}")
            if last_session.get('last_project'):
                print(f"📂 Last project: {last_session['last_project']}")
        
        # Step 3: Determine conversation mode
        mode = self._select_instruction_mode(user_message, last_session)
        print(f"🎯 Selected mode: {mode}")
        
        # Step 4: Load appropriate instructions from brain
        instructions_key = f"{mode}_instructions"
        stored_instructions = self._execute_brain_command(
            "brain_recall", 
            {"query": instructions_key, "limit": 1}
        )
        
        if stored_instructions:
            self.instruction_set = stored_instructions
        else:
            # Use default if not found
            self.instruction_set = self._get_default_instructions(mode)
        
        # Step 5: Load project context if continuing
        if mode == "project_continuation" and last_session and last_session.get('last_project'):
            project_context = self._execute_brain_command(
                "state_get",
                {"category": "project", "key": last_session['last_project']}
            )
            if project_context:
                self.current_project = project_context
                self._display_project_status(project_context)
        
        self.current_session = {
            "started": datetime.now().isoformat(),
            "mode": mode,
            "initial_message": user_message
        }
        
        return last_session, mode
    
    def _select_instruction_mode(self, user_message: str, last_context: Optional[Dict]) -> str:
        """
        Use semantic classification to select appropriate mode.
        In production, this could call Claude to classify.
        """
        # For true semantic routing, we could store a classification prompt
        classification_prompt = f"""
        Classify this user message into one of these modes:
        - project_continuation: User wants to continue existing project work
        - project_management: User wants to start new project or coding task
        - research: User wants to explore or learn about something
        - analysis: User wants to analyze patterns or connections
        - help: User needs help with the system
        - tarot: User wants tarot-related functionality
        - general_assistant: General conversation
        
        User message: "{user_message}"
        Last context: {json.dumps(last_context) if last_context else "None"}
        
        Respond with only the mode name.
        """
        
        # For now, use pattern matching with fallback to semantic
        message_lower = user_message.lower()
        
        # Check for explicit mode switches
        if "switch to" in message_lower:
            for mode in ["research", "project", "analysis", "help"]:
                if mode in message_lower:
                    return mode
        
        # Check for project continuation signals
        if last_context and last_context.get("last_project"):
            continuity_signals = ["continue", "let's", "next", "now", "then", "also", "keep going"]
            if any(signal in message_lower for signal in continuity_signals):
                return "project_continuation"
        
        # Pattern-based classification
        mode_patterns = {
            "project_management": r"\b(project|build|create|implement|fix|debug|code|develop)\b",
            "research": r"\b(research|learn|explore|investigate|how does|what is|explain)\b",
            "analysis": r"\b(analyze|pattern|insight|connection|relationship|trend)\b",
            "help": r"\b(help|how do i|guide|tutorial|documentation)\b",
            "tarot": r"\b(tarot|reading|spread|cards|divination)\b"
        }
        
        for mode, pattern in mode_patterns.items():
            if re.search(pattern, message_lower, re.I):
                return mode
        
        return "general_assistant"
    
    def propose_context_update(self, update_type: str, updates: Dict) -> Dict:
        """
        Generate a proposed context update for human review.
        """
        if not self.current_project:
            return {"error": "No active project", "type": "error"}
        
        # Create proposed update
        proposed = self.current_project.copy()
        
        # Track what's changing
        changes_made = []
        
        if update_type == "progress":
            proposed["last_modified"] = datetime.now().isoformat()
            
            if "completed_tasks" in updates:
                old_tasks = proposed.get("open_tasks", [])
                proposed["open_tasks"] = [
                    task for task in old_tasks
                    if task not in updates["completed_tasks"]
                ]
                changes_made.append(f"Completed {len(updates['completed_tasks'])} tasks")
            
            if "new_tasks" in updates:
                proposed.setdefault("open_tasks", []).extend(updates["new_tasks"])
                changes_made.append(f"Added {len(updates['new_tasks'])} new tasks")
            
            if "current_focus" in updates:
                proposed["current_focus"] = updates["current_focus"]
                changes_made.append(f"Changed focus to: {updates['current_focus']}")
            
            if "summary" in updates:
                proposed["summary"] = updates["summary"]
                changes_made.append("Updated project summary")
        
        elif update_type == "decision":
            decision_entry = {
                "timestamp": datetime.now().isoformat(),
                "decision": updates.get("decision", "Unknown"),
                "rationale": updates.get("rationale", "No rationale provided"),
                "impact": updates.get("impact", "Unknown")
            }
            proposed.setdefault("key_decisions", []).append(decision_entry)
            changes_made.append(f"Recorded decision: {decision_entry['decision']}")
        
        elif update_type == "milestone":
            milestone = {
                "timestamp": datetime.now().isoformat(),
                "title": updates.get("title", "Unnamed milestone"),
                "description": updates.get("description", ""),
                "artifacts": updates.get("artifacts", [])
            }
            proposed.setdefault("milestones", []).append(milestone)
            changes_made.append(f"Added milestone: {milestone['title']}")
        
        # Generate confirmation prompt
        confirmation_prompt = self._generate_confirmation_prompt(
            update_type, changes_made, proposed
        )
        
        return {
            "type": update_type,
            "changes_summary": " | ".join(changes_made),
            "confirmation_prompt": confirmation_prompt,
            "proposed_context": proposed,
            "original_updates": updates
        }
    
    def _generate_confirmation_prompt(self, update_type: str, changes: List[str], context: Dict) -> str:
        """Generate human-friendly confirmation prompt."""
        prompt = f"📝 Proposed {update_type} update for '{context['project_name']}':\n\n"
        
        for change in changes:
            prompt += f"  • {change}\n"
        
        prompt += "\nConfirm these changes? (yes/no/edit): "
        return prompt
    
    def confirm_and_save_update(self, proposed_update: Dict, confirmed: bool = True) -> bool:
        """
        Save the proposed update after human confirmation.
        """
        if not confirmed or "error" in proposed_update:
            print("❌ Update cancelled")
            return False
        
        project_name = proposed_update["proposed_context"]["project_name"]
        
        # Save project context
        result = self._execute_brain_command(
            "state_set",
            {
                "category": "project",
                "key": project_name,
                "value": proposed_update["proposed_context"]
            }
        )
        
        if result:
            print(f"✅ Saved project context for: {project_name}")
            self.current_project = proposed_update["proposed_context"]
            
            # Update session context
            session_update = {
                "timestamp": datetime.now().isoformat(),
                "last_project": project_name,
                "last_activity": proposed_update["changes_summary"],
                "conversation_mode": self.instruction_set.get("name", "unknown"),
                "open_tasks": self.current_project.get("open_tasks", []),
                "key_decisions": [
                    d["decision"] if isinstance(d, dict) else d 
                    for d in self.current_project.get("key_decisions", [])[-3:]  # Last 3
                ]
            }
            
            self._execute_brain_command(
                "state_set",
                {
                    "category": "system",
                    "key": "last_session_context",
                    "value": session_update
                }
            )
            
            return True
        
        return False
    
    def create_obsidian_dashboard(self, project_name: str, save_to_vault: bool = False) -> str:
        """
        Generate an Obsidian dashboard note for the project.
        """
        # Get project context
        context = self._execute_brain_command(
            "state_get",
            {"category": "project", "key": project_name}
        )
        
        if not context:
            context = {"project_name": project_name, "status": "not_found"}
        
        # Generate dashboard content
        dashboard = f"""# {context.get('project_name', project_name)}

> **Status:** {context.get('status', 'Unknown')} | **Last Modified:** {context.get('last_modified', 'Never')}

## 📋 Summary
{context.get('summary', '*No summary available*')}

## 🎯 Current Focus
{context.get('current_focus', '*Focus not set*')}

## ✅ Open Tasks
"""
        
        tasks = context.get('open_tasks', [])
        if tasks:
            for task in tasks:
                dashboard += f"- [ ] {task}\n"
        else:
            dashboard += "*No open tasks*\n"
        
        dashboard += "\n## 🔨 Recent Milestones\n"
        milestones = context.get('milestones', [])
        if milestones:
            for milestone in milestones[-3:]:  # Last 3
                if isinstance(milestone, dict):
                    dashboard += f"- **{milestone.get('title', 'Untitled')}** - {milestone.get('timestamp', 'Unknown date')}\n"
                    if milestone.get('description'):
                        dashboard += f"  - {milestone['description']}\n"
        else:
            dashboard += "*No milestones recorded*\n"
        
        dashboard += "\n## 💡 Key Decisions\n"
        decisions = context.get('key_decisions', [])
        if decisions:
            for decision in decisions[-5:]:  # Last 5
                if isinstance(decision, dict):
                    dashboard += f"- **{decision.get('decision', 'Unknown')}**\n"
                    dashboard += f"  - *Rationale:* {decision.get('rationale', 'Not provided')}\n"
                    dashboard += f"  - *When:* {decision.get('timestamp', 'Unknown')}\n"
                else:
                    dashboard += f"- {decision}\n"
        else:
            dashboard += "*No decisions recorded*\n"
        
        dashboard += "\n## 📁 Key Files\n"
        files = context.get('key_files', [])
        if files:
            for file in files:
                # Make it an Obsidian link
                file_name = file.split('/')[-1]
                dashboard += f"- [[{file_name}]] - `{file}`\n"
        else:
            dashboard += "*No key files tracked*\n"
        
        dashboard += "\n## 🔗 Related Resources\n"
        if context.get('dependencies'):
            deps = context['dependencies']
            if deps.get('obsidian_notes'):
                dashboard += "### Obsidian Notes\n"
                for note in deps['obsidian_notes']:
                    dashboard += f"- [[{note}]]\n"
            if deps.get('related_projects'):
                dashboard += "### Related Projects\n"
                for proj in deps['related_projects']:
                    dashboard += f"- [[{proj}]]\n"
        
        dashboard += f"\n---\n*Dashboard generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
        
        if save_to_vault:
            # Save to Obsidian
            result = self._execute_brain_command(
                "obsidian_note",
                {
                    "action": "create",
                    "title": f"{project_name} - Dashboard",
                    "content": dashboard,
                    "folder": "Projects"
                }
            )
            if result:
                print(f"✅ Saved dashboard to Obsidian: {project_name} - Dashboard")
        
        return dashboard
    
    def switch_project(self, new_project_name: str) -> bool:
        """
        Switch to a different project, implementing session stack.
        """
        # Save current to stack
        if self.current_project:
            print(f"📥 Saving '{self.current_project['project_name']}' to session stack")
            
            # Create a snapshot of current state
            snapshot = {
                "project": self.current_project.copy(),
                "instruction_set": self.instruction_set,
                "timestamp": datetime.now().isoformat(),
                "session_data": {
                    "duration": self._calculate_session_duration(),
                    "mode": self.current_session.get("mode", "unknown")
                }
            }
            self.session_stack.append(snapshot)
            
            # Also save to state for persistence
            self._execute_brain_command(
                "state_set",
                {
                    "category": "session",
                    "key": "project_stack",
                    "value": self.session_stack
                }
            )
        
        # Load new project
        new_context = self._execute_brain_command(
            "state_get",
            {"category": "project", "key": new_project_name}
        )
        
        if new_context:
            self.current_project = new_context
            self.instruction_set = self._get_default_instructions("project_continuation")
            print(f"✅ Switched to project: {new_project_name}")
            self._display_project_status(new_context)
            return True
        else:
            print(f"❌ Project not found: {new_project_name}")
            print("Would you like to create it? Use: create_new_project()")
            return False
    
    def return_to_previous_project(self) -> bool:
        """Pop and restore previous project from stack."""
        if not self.session_stack:
            # Try to load from state
            saved_stack = self._execute_brain_command(
                "state_get",
                {"category": "session", "key": "project_stack"}
            )
            if saved_stack:
                self.session_stack = saved_stack
        
        if not self.session_stack:
            print("❌ No previous project in stack")
            return False
        
        # Pop the most recent
        snapshot = self.session_stack.pop()
        self.current_project = snapshot["project"]
        self.instruction_set = snapshot["instruction_set"]
        
        print(f"↩️  Returned to: {self.current_project['project_name']}")
        print(f"⏰ Saved at: {snapshot['timestamp']}")
        self._display_project_status(self.current_project)
        
        # Update saved stack
        self._execute_brain_command(
            "state_set",
            {
                "category": "session",
                "key": "project_stack",
                "value": self.session_stack
            }
        )
        
        return True
    
    def _display_project_status(self, project: Dict):
        """Display project status in a nice format."""
        print(f"\n📊 Project Status: {project['project_name']}")
        print(f"   Status: {project.get('status', 'Unknown')}")
        print(f"   Focus: {project.get('current_focus', 'Not set')}")
        
        tasks = project.get('open_tasks', [])
        if tasks:
            print(f"   Open tasks: {len(tasks)}")
            for task in tasks[:3]:  # Show first 3
                print(f"     - {task}")
            if len(tasks) > 3:
                print(f"     ... and {len(tasks) - 3} more")
    
    def _calculate_session_duration(self) -> str:
        """Calculate how long the current session has been active."""
        if not self.current_session or "started" not in self.current_session:
            return "unknown"
        
        start = datetime.fromisoformat(self.current_session["started"])
        duration = datetime.now() - start
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _execute_brain_command(self, command: str, params: Optional[Dict] = None):
        """
        Execute a brain tool command.
        In production, this would call the actual tools.
        For testing, we'll simulate responses.
        """
        print(f"🔧 Executing: brain:{command}" + (f" with {params}" if params else ""))
        
        # In production, this would make actual tool calls
        # For now, return mock data for testing
        if command == "brain_init":
            return True
        elif command == "state_get":
            # Simulate some responses
            if params.get("key") == "last_session_context":
                return {
                    "timestamp": "2025-01-07T10:30:00Z",
                    "last_project": "brain_system_design",
                    "last_activity": "Implementation planning"
                }
            elif params.get("key") == "brain_system_design":
                return {
                    "project_name": "brain_system_design",
                    "status": "active",
                    "summary": "Brain Knowledge Management System",
                    "current_focus": "Creating management layer",
                    "open_tasks": ["Test implementation", "Create documentation"],
                    "key_decisions": []
                }
        elif command == "brain_recall":
            return None  # No stored instructions yet
        
        return None
    
    def _get_default_instructions(self, mode: str) -> Dict:
        """Get default instruction set for a mode."""
        defaults = {
            "project_continuation": {
                "name": "Project Continuation",
                "behaviors": [
                    "Load and display project context",
                    "Show progress since last session",
                    "Focus on open tasks",
                    "Update context after significant changes"
                ]
            },
            "general_assistant": {
                "name": "General Assistant",
                "behaviors": [
                    "Be helpful and informative",
                    "Identify if this relates to a project",
                    "Suggest relevant tools or resources"
                ]
            }
        }
        return defaults.get(mode, defaults["general_assistant"])


# Convenience functions for direct use
def init_brain_manager(message: str = "") -> BrainSystemManager:
    """Initialize and return a configured Brain System Manager."""
    manager = BrainSystemManager()
    manager.enhanced_brain_init(message)
    return manager


if __name__ == "__main__":
    # Example usage
    print("Brain System Manager - Test Run\n")
    
    # Initialize
    manager = init_brain_manager("Let's continue working on the brain system")
    
    # Test update proposal
    update = manager.propose_context_update("progress", {
        "completed_tasks": ["Design the system"],
        "new_tasks": ["Write tests", "Create documentation"],
        "current_focus": "Implementation phase"
    })
    
    print(f"\n{update['confirmation_prompt']}")
    
    # Test dashboard generation
    dashboard = manager.create_obsidian_dashboard("brain_system_design")
    print("\n📄 Generated Dashboard Preview:")
    print(dashboard[:400] + "...")

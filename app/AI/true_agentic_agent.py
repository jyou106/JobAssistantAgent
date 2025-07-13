import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
from fireworks.client import Fireworks
from .scraper import scrape_job_description
from .scorer import score_resume
import os
from dotenv import load_dotenv

load_dotenv()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
fw = Fireworks(api_key=FIREWORKS_API_KEY)

class AgentGoal(Enum):
    CAREER_ADVANCEMENT = "career_advancement"
    SKILL_DEVELOPMENT = "skill_development"
    NETWORK_BUILDING = "network_building"
    SALARY_IMPROVEMENT = "salary_improvement"
    WORK_LIFE_BALANCE = "work_life_balance"

class AgentAction(Enum):
    ANALYZE_RESUME = "analyze_resume"
    SUGGEST_IMPROVEMENTS = "suggest_improvements"
    RECOMMEND_JOBS = "recommend_jobs"
    PLAN_SKILL_DEALS = "plan_skill_development"
    SUGGEST_NETWORKING = "suggest_networking"
    TRACK_PROGRESS = "track_progress"
    ADAPT_STRATEGY = "adapt_strategy"
    SCORE_RESUME = "score_resume"
    GENERATE_TAILORED_ANSWERS = "generate_tailored_answers"

@dataclass
class AgentMemory:
    user_id: str
    interactions: List[Dict] = field(default_factory=list)
    goals: List[AgentGoal] = field(default_factory=list)
    strategies: List[Dict] = field(default_factory=list)
    outcomes: List[Dict] = field(default_factory=list)
    preferences: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class AgentContext:
    current_situation: Dict[str, Any]
    goals: List[AgentGoal]
    memory: AgentMemory
    available_actions: List[AgentAction]
    constraints: Dict[str, Any]

class TrueAgenticCareerAgent:
    """
    A truly agentic career assistant that:
    - Makes autonomous decisions
    - Pursues goals independently
    - Learns from outcomes
    - Adapts strategies
    - Takes proactive actions
    """
    
    def __init__(self):
        self.memories: Dict[str, AgentMemory] = {}
        self.global_learning: Dict[str, Any] = {
            "successful_strategies": [],
            "common_obstacles": [],
            "market_trends": [],
            "skill_demands": []
        }
    
    def get_or_create_memory(self, user_id: str) -> AgentMemory:
        """Get existing memory or create new one for user"""
        if user_id not in self.memories:
            self.memories[user_id] = AgentMemory(user_id=user_id)
        return self.memories[user_id]
    
    def autonomous_workflow(self, user_id: str, resume_text: str, job_url: str = None, questions: List[str] = None, recursion_depth: int = 0) -> Dict[str, Any]:
        """
        Main autonomous workflow - agent decides what to do
        """
        # Safety check to prevent infinite recursion
        if recursion_depth > 3:
            return {
                "success": False,
                "error": "Maximum recursion depth exceeded",
                "fallback_to_basic": True
            }
        
        memory = self.get_or_create_memory(user_id)
        
        # Store resume text in memory for future reference
        memory.interactions.append({
            "timestamp": datetime.now(),
            "resume_text": resume_text,
            "job_url": job_url,
            "questions": questions
        })
        
        # Step 1: Agent analyzes current situation
        situation = self.analyze_current_situation(resume_text, job_url, memory)
        
        # Add job URL and questions to situation for core functionalities
        if job_url:
            situation["job_url"] = job_url
        if questions:
            situation["questions"] = questions
        
        # Step 2: Agent identifies goals and obstacles
        goals = self.identify_goals(situation, memory)
        obstacles = self.identify_obstacles(situation, goals)
        
        # Step 3: Agent decides on actions to take
        actions = self.decide_actions(situation, goals, obstacles, memory)
        
        # Step 4: Agent executes actions
        results = self.execute_actions(actions, situation, memory)
        
        # Step 5: Agent learns from outcomes
        self.learn_from_outcome(results, memory)
        
        # Step 6: Agent adapts strategy (already handled in execute_actions)
        
        # Organize results to eliminate redundancy
        organized_results = self.organize_results(results, situation)
        
        return {
            "success": True,
            "autonomous_analysis": situation,
            "agent_goals": [goal.value for goal in goals],
            "identified_obstacles": obstacles,
            "agent_actions": [action.value for action in actions],
            "execution_results": organized_results,
            "learning_applied": True,
            "strategy_adaptation": self.get_strategy_adaptation(memory)
        }
    
    def analyze_current_situation(self, resume_text: str, job_url: str, memory: AgentMemory) -> Dict[str, Any]:
        """Agent autonomously analyzes the current situation"""
        try:
            # Analyze resume with optional job matching
            resume_analysis = self.analyze_resume_autonomously(resume_text, job_url)
            
            # Analyze market if job URL provided
            market_analysis = {}
            if job_url:
                market_analysis = self.analyze_market_autonomously(job_url)
            
            # Analyze user's career trajectory
            career_trajectory = self.analyze_career_trajectory(memory)
            
            # Detect opportunities and threats
            opportunities = self.detect_opportunities(resume_analysis, market_analysis)
            threats = self.detect_threats(resume_analysis, market_analysis)
            
            return {
                "resume_strength": resume_analysis.get("strength_score", 0),
                "market_opportunity": market_analysis.get("opportunity_score", 0),
                "career_stage": career_trajectory.get("stage", "early_career"),
                "skill_gaps": resume_analysis.get("skill_gaps", []),
                "opportunities": opportunities,
                "threats": threats,
                "recommended_focus": self.determine_focus_area(resume_analysis, market_analysis)
            }
        except Exception as e:
            logging.error(f"Situation analysis failed: {e}")
            return {"error": str(e)}
    
    def identify_goals(self, situation: Dict[str, Any], memory: AgentMemory) -> List[AgentGoal]:
        """Agent autonomously identifies goals based on situation"""
        goals = []
        
        # Analyze situation to determine goals
        if situation.get("resume_strength", 0) < 0.7:
            goals.append(AgentGoal.SKILL_DEVELOPMENT)
        
        if situation.get("market_opportunity", 0) > 0.8:
            goals.append(AgentGoal.CAREER_ADVANCEMENT)
        
        if len(memory.interactions) < 5:
            goals.append(AgentGoal.NETWORK_BUILDING)
        
        # Add salary improvement if user has been in role for long
        if memory.outcomes and any(outcome.get("salary_level") == "below_market" for outcome in memory.outcomes):
            goals.append(AgentGoal.SALARY_IMPROVEMENT)
        
        # Default goal if none identified
        if not goals:
            goals.append(AgentGoal.CAREER_ADVANCEMENT)
        
        return goals
    
    def identify_obstacles(self, situation: Dict[str, Any], goals: List[AgentGoal]) -> List[str]:
        """Agent identifies obstacles to achieving goals"""
        obstacles = []
        
        if situation.get("resume_strength", 0) < 0.6:
            obstacles.append("weak_resume")
        
        if situation.get("skill_gaps"):
            obstacles.append("skill_gaps")
        
        if situation.get("market_opportunity", 0) < 0.5:
            obstacles.append("limited_market_opportunity")
        
        if AgentGoal.NETWORK_BUILDING in goals and len(self.memories) < 3:
            obstacles.append("limited_network")
        
        return obstacles
    
    def decide_actions(self, situation: Dict[str, Any], goals: List[AgentGoal], 
                      obstacles: List[str], memory: AgentMemory) -> List[AgentAction]:
        """Agent autonomously decides what actions to take"""
        actions = []
        
        # Always analyze and track progress
        actions.append(AgentAction.ANALYZE_RESUME)
        actions.append(AgentAction.TRACK_PROGRESS)
        
        # Add goal-specific actions
        for goal in goals:
            if goal == AgentGoal.SKILL_DEVELOPMENT:
                actions.append(AgentAction.PLAN_SKILL_DEALS)
            elif goal == AgentGoal.CAREER_ADVANCEMENT:
                actions.append(AgentAction.RECOMMEND_JOBS)
            elif goal == AgentGoal.NETWORK_BUILDING:
                actions.append(AgentAction.SUGGEST_NETWORKING)
        
        # Add obstacle-specific actions
        if "weak_resume" in obstacles:
            actions.append(AgentAction.SUGGEST_IMPROVEMENTS)
        
        if "skill_gaps" in obstacles:
            actions.append(AgentAction.PLAN_SKILL_DEALS)
        
        # Add core functionalities when job URL is available
        if situation.get("job_url"):
            actions.append(AgentAction.SCORE_RESUME)
            
            # Add tailored answers if questions are provided
            if situation.get("questions"):
                actions.append(AgentAction.GENERATE_TAILORED_ANSWERS)
        
        # Adapt strategy only if there are previous outcomes and recent failures
        # This prevents recursion on first run when no outcomes exist
        if (memory.outcomes and 
            len(memory.outcomes) >= 3 and 
            any(outcome.get("success") == False for outcome in memory.outcomes[-3:])):
            actions.append(AgentAction.ADAPT_STRATEGY)
        
        return list(set(actions))  # Remove duplicates
    
    def execute_actions(self, actions: List[AgentAction], situation: Dict[str, Any], 
                       memory: AgentMemory) -> Dict[str, Any]:
        """Agent executes the decided actions"""
        results = {}
        
        # Separate ADAPT_STRATEGY from other actions to prevent recursion
        strategy_adaptation_needed = AgentAction.ADAPT_STRATEGY in actions
        other_actions = [action for action in actions if action != AgentAction.ADAPT_STRATEGY]
        
        # Execute all actions except ADAPT_STRATEGY
        for action in other_actions:
            if action == AgentAction.ANALYZE_RESUME:
                results["resume_analysis"] = self.perform_resume_analysis(situation)
            
            elif action == AgentAction.SUGGEST_IMPROVEMENTS:
                results["improvements"] = self.suggest_improvements(situation, memory)
            
            elif action == AgentAction.RECOMMEND_JOBS:
                results["job_recommendations"] = self.recommend_jobs(situation, memory)
            
            elif action == AgentAction.PLAN_SKILL_DEALS:
                results["skill_development"] = self.plan_skill_development(situation, memory)
            
            elif action == AgentAction.SUGGEST_NETWORKING:
                results["networking"] = self.suggest_networking(situation, memory)
            
            elif action == AgentAction.TRACK_PROGRESS:
                results["progress"] = self.track_progress(memory)
            
            elif action == AgentAction.SCORE_RESUME:
                results["resume_scoring"] = self.perform_resume_scoring(situation, memory)
            
            elif action == AgentAction.GENERATE_TAILORED_ANSWERS:
                results["tailored_answers"] = self.generate_tailored_answers(situation, memory)
        
        # Execute ADAPT_STRATEGY separately after all other actions are complete
        if strategy_adaptation_needed:
            self.adapt_strategy(memory, results)
            results["strategy_adaptation"] = {
                "status": "adapted",
                "timestamp": datetime.now().isoformat()
            }
        
        return results
    
    def perform_resume_analysis(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed resume analysis"""
        return {
            "strength_score": situation.get("resume_strength", 0),
            "skill_gaps": situation.get("skill_gaps", []),
            "opportunities": situation.get("opportunities", []),
            "threats": situation.get("threats", []),
            "recommended_focus": situation.get("recommended_focus", "balanced_improvement")
        }
    
    def analyze_career_trajectory(self, memory: AgentMemory) -> Dict[str, Any]:
        """Analyze user's career trajectory based on memory"""
        if not memory.outcomes:
            return {"stage": "early_career", "experience_level": "entry"}
        
        # Analyze recent outcomes to determine career stage
        recent_outcomes = memory.outcomes[-5:] if memory.outcomes else []
        success_rate = sum(1 for outcome in recent_outcomes 
                          if outcome.get("success_indicators", {}).get("overall_success", False)) / len(recent_outcomes) if recent_outcomes else 0
        
        if success_rate > 0.8:
            return {"stage": "advanced_career", "experience_level": "senior"}
        elif success_rate > 0.5:
            return {"stage": "mid_career", "experience_level": "mid"}
        else:
            return {"stage": "early_career", "experience_level": "entry"}
    
    def detect_opportunities(self, resume_analysis: Dict[str, Any], market_analysis: Dict[str, Any]) -> List[str]:
        """Detect opportunities based on resume and market analysis"""
        opportunities = []
        
        if resume_analysis.get("strength_score", 0) > 0.7:
            opportunities.append("strong_resume")
        
        if market_analysis.get("opportunity_score", 0) > 0.8:
            opportunities.append("high_market_opportunity")
        
        if resume_analysis.get("skill_gaps"):
            opportunities.append("skill_development_potential")
        
        return opportunities
    
    def detect_threats(self, resume_analysis: Dict[str, Any], market_analysis: Dict[str, Any]) -> List[str]:
        """Detect threats based on resume and market analysis"""
        threats = []
        
        if resume_analysis.get("strength_score", 0) < 0.6:
            threats.append("weak_resume")
        
        if market_analysis.get("opportunity_score", 0) < 0.5:
            threats.append("limited_market_opportunity")
        
        if resume_analysis.get("skill_gaps"):
            threats.append("skill_gaps")
        
        return threats
    
    def develop_new_strategy(self, memory: AgentMemory, results: Dict[str, Any]) -> str:
        """Develop a new strategy based on learning"""
        if not memory.outcomes:
            return "balanced"
        
        # Analyze recent outcomes to determine new strategy
        recent_outcomes = memory.outcomes[-3:] if memory.outcomes else []
        failure_count = sum(1 for outcome in recent_outcomes 
                           if not outcome.get("success_indicators", {}).get("overall_success", False))
        
        if failure_count > 1:
            return "aggressive"  # Need to be more aggressive
        else:
            return "balanced"  # Stay balanced
    
    def learn_from_outcome(self, results: Dict[str, Any], memory: AgentMemory):
        """Agent learns from the outcomes of its actions"""
        learning_entry = {
            "timestamp": datetime.now(),
            "actions_taken": list(results.keys()),
            "outcomes": results,
            "success_indicators": self.extract_success_indicators(results),
            "lessons_learned": self.extract_lessons(results)
        }
        
        memory.outcomes.append(learning_entry)
        memory.last_updated = datetime.now()
        
        # Update global learning
        self.update_global_learning(learning_entry)
    
    def adapt_strategy(self, memory: AgentMemory, results: Dict[str, Any]):
        """Agent adapts its strategy based on outcomes"""
        # Safety check: only adapt if there are outcomes and we haven't adapted recently
        if not memory.outcomes or len(memory.outcomes) < 2:
            return
        
        # Check if we've already adapted recently (within last 5 minutes)
        recent_strategies = [s for s in memory.strategies 
                           if (datetime.now() - s.get("timestamp", datetime.now())).total_seconds() < 300]
        if recent_strategies:
            return
        
        # Analyze recent outcomes
        recent_outcomes = memory.outcomes[-5:] if memory.outcomes else []
        
        if recent_outcomes:
            success_rate = sum(1 for outcome in recent_outcomes 
                             if outcome.get("success_indicators", {}).get("overall_success", False)) / len(recent_outcomes)
            
            if success_rate < 0.5:
                # Strategy not working, adapt
                new_strategy = self.develop_new_strategy(memory, results)
                memory.strategies.append({
                    "timestamp": datetime.now(),
                    "strategy": new_strategy,
                    "reason": "low_success_rate",
                    "expected_improvement": "high"
                })
    
    def analyze_resume_autonomously(self, resume_text: str, job_url: str = None) -> Dict[str, Any]:
        """Agent autonomously analyzes resume with optional job matching"""
        try:
            prompt = f"""
            Analyze this resume autonomously and provide insights:
            {resume_text}
            
            Return JSON with:
            - strength_score: 0-1 score of resume strength
            - skill_gaps: [list of missing skills]
            - strengths: [list of strong areas]
            - experience_level: "entry", "mid", "senior"
            - industry_fit: "tech", "finance", "healthcare", etc.
            - improvement_priority: "high", "medium", "low"
            """
            
            response = fw.chat.completions.create(
                model="accounts/fireworks/models/llama-v3p1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_str = response.choices[0].message.content.strip()
            import re
            json_match = re.search(r"\{[\s\S]*\}", result_str)
            if json_match:
                basic_analysis = json.loads(json_match.group(0))
            else:
                basic_analysis = {
                    "strength_score": 0.7,
                    "skill_gaps": ["advanced_ml", "leadership"],
                    "strengths": ["technical_skills", "research"],
                    "experience_level": "mid",
                    "industry_fit": "tech",
                    "improvement_priority": "medium"
                }
            
            # If job URL provided, get detailed match score and insights
            if job_url:
                try:
                    from .scorer import score_resume
                    scoring_result = score_resume(resume_text, job_url)
                    basic_analysis["match_score"] = scoring_result.get("match_score")
                    basic_analysis["insights"] = scoring_result.get("insights", [])
                except Exception as e:
                    logging.error(f"Job matching failed: {e}")
                    # Continue with basic analysis if job matching fails
            
            return basic_analysis
        except Exception as e:
            logging.error(f"Resume analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_market_autonomously(self, job_url: str) -> Dict[str, Any]:
        """Agent autonomously analyzes market opportunities"""
        try:
            job_desc = scrape_job_description(job_url)
            
            prompt = f"""
            Analyze this job market autonomously:
            {job_desc}
            
            Return JSON with:
            - opportunity_score: 0-1 score of opportunity
            - market_demand: "high", "medium", "low"
            - salary_potential: "high", "medium", "low"
            - growth_potential: "high", "medium", "low"
            - competitive_level: "high", "medium", "low"
            """
            
            response = fw.chat.completions.create(
                model="accounts/fireworks/models/llama-v3p1-8b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            result_str = response.choices[0].message.content.strip()
            import re
            json_match = re.search(r"\{[\s\S]*\}", result_str)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {
                    "opportunity_score": 0.8,
                    "market_demand": "high",
                    "salary_potential": "high",
                    "growth_potential": "high",
                    "competitive_level": "high"
                }
        except Exception as e:
            logging.error(f"Market analysis failed: {e}")
            return {"error": str(e)}
    
    def suggest_improvements(self, situation: Dict[str, Any], memory: AgentMemory) -> List[Dict[str, Any]]:
        """Agent autonomously suggests improvements"""
        improvements = []
        
        if situation.get("resume_strength", 0) < 0.7:
            improvements.append({
                "type": "resume",
                "priority": "high",
                "suggestion": "Add more quantifiable achievements",
                "expected_impact": 0.8,
                "timeline": "1-2 weeks"
            })
        
        if situation.get("skill_gaps"):
            for skill in situation["skill_gaps"][:3]:  # Top 3 gaps
                improvements.append({
                    "type": "skill_development",
                    "priority": "medium",
                    "suggestion": f"Develop expertise in {skill}",
                    "expected_impact": 0.7,
                    "timeline": "2-3 months"
                })
        
        return improvements
    
    def recommend_jobs(self, situation: Dict[str, Any], memory: AgentMemory) -> List[Dict[str, Any]]:
        """Agent autonomously recommends jobs"""
        # This would integrate with job APIs in a real implementation
        return [
            {
                "title": "Senior ML Engineer",
                "company": "Tech Company",
                "match_score": 0.85,
                "reason": "Strong ML background matches requirements",
                "priority": "high"
            },
            {
                "title": "Data Scientist",
                "company": "AI Startup",
                "match_score": 0.78,
                "reason": "Research background valuable for startup",
                "priority": "medium"
            }
        ]
    
    def plan_skill_development(self, situation: Dict[str, Any], memory: AgentMemory) -> Dict[str, Any]:
        """Agent autonomously plans skill development"""
        skill_gaps = situation.get("skill_gaps", [])
        
        plan = {
            "timeline": "3-6 months",
            "skills_to_develop": skill_gaps[:3],
            "learning_resources": [],
            "milestones": [],
            "expected_outcomes": []
        }
        
        for skill in skill_gaps[:3]:
            plan["learning_resources"].append({
                "skill": skill,
                "resources": [f"Online course for {skill}", f"Project in {skill}"],
                "timeline": "2-3 months"
            })
        
        return plan
    
    def suggest_networking(self, situation: Dict[str, Any], memory: AgentMemory) -> List[Dict[str, Any]]:
        """Agent autonomously suggests networking opportunities"""
        return [
            {
                "type": "professional_group",
                "name": "ML Engineers Network",
                "reason": "Aligns with career goals",
                "priority": "high"
            },
            {
                "type": "conference",
                "name": "AI/ML Conference",
                "reason": "Stay updated with industry trends",
                "priority": "medium"
            }
        ]
    
    def track_progress(self, memory: AgentMemory) -> Dict[str, Any]:
        """Agent autonomously tracks progress"""
        if not memory.outcomes:
            return {"status": "new_user", "progress": 0}
        
        recent_outcomes = memory.outcomes[-5:]
        success_rate = sum(1 for outcome in recent_outcomes 
                          if outcome.get("success_indicators", {}).get("overall_success", False)) / len(recent_outcomes)
        
        return {
            "overall_progress": success_rate,
            "recent_improvements": len([o for o in recent_outcomes if o.get("success_indicators", {}).get("improvement", False)]),
            "goals_achieved": len([o for o in recent_outcomes if o.get("success_indicators", {}).get("goal_achieved", False)]),
            "next_milestone": self.determine_next_milestone(memory)
        }
    
    def extract_success_indicators(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Agent extracts success indicators from results"""
        return {
            "overall_success": len(results) > 0,
            "improvement": any("improvement" in str(v).lower() for v in results.values()),
            "goal_achieved": any("goal" in str(v).lower() for v in results.values()),
            "action_completed": len(results)
        }
    
    def extract_lessons(self, results: Dict[str, Any]) -> List[str]:
        """Agent extracts lessons learned from results"""
        lessons = []
        
        if "resume_analysis" in results:
            lessons.append("Resume analysis completed successfully")
        
        if "improvements" in results:
            lessons.append("Improvement suggestions generated")
        
        if "job_recommendations" in results:
            lessons.append("Job recommendations provided")
        
        return lessons
    
    def update_global_learning(self, learning_entry: Dict[str, Any]):
        """Agent updates global learning from all users"""
        # Update successful strategies
        if learning_entry.get("success_indicators", {}).get("overall_success"):
            self.global_learning["successful_strategies"].append({
                "timestamp": datetime.now(),
                "strategy": learning_entry.get("actions_taken", []),
                "outcome": "success"
            })
        
        # Update common obstacles
        if learning_entry.get("outcomes", {}).get("obstacles"):
            self.global_learning["common_obstacles"].extend(
                learning_entry["outcomes"]["obstacles"]
            )
    
    def get_strategy_adaptation(self, memory: AgentMemory) -> Dict[str, Any]:
        """Get current strategy adaptation"""
        if not memory.strategies:
            return {"status": "initial_strategy", "adaptations": 0}
        
        latest_strategy = memory.strategies[-1]
        return {
            "current_strategy": latest_strategy.get("strategy", "balanced"),
            "adaptation_reason": latest_strategy.get("reason", "initial"),
            "expected_improvement": latest_strategy.get("expected_improvement", "medium"),
            "total_adaptations": len(memory.strategies)
        }
    
    def determine_focus_area(self, resume_analysis: Dict[str, Any], market_analysis: Dict[str, Any]) -> str:
        """Agent determines focus area based on analysis"""
        resume_strength = resume_analysis.get("strength_score", 0)
        market_opportunity = market_analysis.get("opportunity_score", 0)
        
        if resume_strength < 0.6:
            return "skill_development"
        elif market_opportunity > 0.8:
            return "career_advancement"
        else:
            return "balanced_improvement"
    
    def determine_next_milestone(self, memory: AgentMemory) -> str:
        """Agent determines next milestone"""
        if not memory.outcomes:
            return "complete_initial_assessment"
        
        recent_progress = self.track_progress(memory)
        
        if recent_progress["overall_progress"] < 0.5:
            return "improve_basic_skills"
        elif recent_progress["goals_achieved"] < 2:
            return "achieve_career_goals"
        else:
            return "advance_to_next_level"
    
    def perform_resume_scoring(self, situation: Dict[str, Any], memory: AgentMemory) -> Dict[str, Any]:
        """Agent performs detailed resume scoring against job posting"""
        try:
            # This would be called when job URL is available
            if "job_url" in situation:
                from .scorer import score_resume
                resume_text = memory.interactions[-1].get("resume_text") if memory.interactions else ""
                job_url = situation["job_url"]
                
                scoring_result = score_resume(resume_text, job_url)
                return {
                    "match_score": scoring_result.get("match_score"),
                    "insights": scoring_result.get("insights", []),
                    "scoring_method": "ATS-style",
                    "confidence": "high"
                }
            else:
                return {
                    "error": "No job URL provided for scoring",
                    "scoring_method": "basic_analysis"
                }
        except Exception as e:
            logging.error(f"Resume scoring failed: {e}")
            return {"error": str(e)}
    
    def generate_tailored_answers(self, situation: Dict[str, Any], memory: AgentMemory) -> Dict[str, Any]:
        """Agent generates tailored answers for application questions"""
        try:
            # This would be called when job URL and questions are available
            if "job_url" in situation and "questions" in situation:
                from .tailored_answer import tailored_answer
                resume_text = memory.interactions[-1].get("resume_text") if memory.interactions else ""
                job_url = situation["job_url"]
                questions = situation["questions"]
                
                answer_result = tailored_answer(resume_text, job_url, questions)
                
                if answer_result.get("success"):
                    return {
                        "answers": answer_result["data"].get("answers", []),
                        "overall_quality_score": answer_result["data"].get("overall_quality_score"),
                        "generation_method": "AI-tailored",
                        "confidence": "high"
                    }
                else:
                    return {
                        "error": answer_result.get("error", "Unknown error"),
                        "generation_method": "basic_template"
                    }
            else:
                return {
                    "error": "Missing job URL or questions for tailored answers",
                    "generation_method": "basic_template"
                }
        except Exception as e:
            logging.error(f"Tailored answer generation failed: {e}")
            return {"error": str(e)}
    
    def organize_results(self, results: Dict[str, Any], situation: Dict[str, Any]) -> Dict[str, Any]:
        """Organize execution results with logical grouping"""
        organized = {}
        
        # 1. RESUME & JOB MATCHING SECTION
        resume_job_section = {}
        
        # Core resume analysis
        if "resume_analysis" in results:
            resume_job_section["resume_analysis"] = {
                "strength_score": results["resume_analysis"].get("strength_score"),
                "skill_gaps": results["resume_analysis"].get("skill_gaps", []),
                "opportunities": results["resume_analysis"].get("opportunities", []),
                "threats": results["resume_analysis"].get("threats", []),
                "recommended_focus": results["resume_analysis"].get("recommended_focus")
            }
        
        # Job matching results (from scoring)
        if "resume_scoring" in results:
            resume_job_section["job_matching"] = {
                "match_score": results["resume_scoring"].get("match_score"),
                "insights": results["resume_scoring"].get("insights", []),
                "scoring_method": results["resume_scoring"].get("scoring_method"),
                "confidence": results["resume_scoring"].get("confidence")
            }
        
        # Tailored answers (if available)
        if "tailored_answers" in results:
            resume_job_section["tailored_answers"] = {
                "answers": results["tailored_answers"].get("answers", []),
                "overall_quality_score": results["tailored_answers"].get("overall_quality_score"),
                "generation_method": results["tailored_answers"].get("generation_method"),
                "confidence": results["tailored_answers"].get("confidence")
            }
        
        if resume_job_section:
            organized["resume_and_job_matching"] = resume_job_section
        
        # 2. SKILL DEVELOPMENT SECTION (appears after skill gaps are identified)
        if "skill_development" in results:
            organized["skill_development"] = results["skill_development"]
        
        # 3. CAREER DEVELOPMENT SECTION
        career_dev_section = {}
        
        # Networking suggestions
        if "networking" in results:
            career_dev_section["networking"] = results["networking"]
        
        # Progress tracking
        if "progress" in results:
            career_dev_section["progress"] = results["progress"]
        
        if career_dev_section:
            organized["career_development"] = career_dev_section
        
        # 4. AGENT LEARNING SECTION
        agent_section = {}
        
        # Strategy adaptation
        if "strategy_adaptation" in results:
            agent_section["strategy_adaptation"] = results["strategy_adaptation"]
        
        if agent_section:
            organized["agent_learning"] = agent_section
        
        return organized

# Global agent instance
true_agentic_agent = TrueAgenticCareerAgent()

def autonomous_career_workflow(user_id: str, resume_text: str, job_url: str = None, questions: List[str] = None) -> Dict[str, Any]:
    """Main entry point for autonomous career agent"""
    try:
        result = true_agentic_agent.autonomous_workflow(user_id, resume_text, job_url, questions, recursion_depth=0)
        return result
    except Exception as e:
        logging.error(f"Autonomous workflow failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback_to_enhanced": True
        } 
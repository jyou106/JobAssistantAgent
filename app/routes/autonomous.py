from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Any
from app.AI.true_agentic_agent import autonomous_career_workflow, true_agentic_agent
import asyncio
import uuid

router = APIRouter()

class AutonomousAnalysisRequest(BaseModel):
    resume_text: str
    job_posting_url: Optional[HttpUrl] = None
    user_id: Optional[str] = None
    questions: Optional[List[str]] = None

class AutonomousAnalysisResponse(BaseModel):
    success: bool
    autonomous_analysis: Dict[str, Any]
    agent_goals: List[str]
    identified_obstacles: List[str]
    agent_actions: List[str]
    execution_results: Dict[str, Any]
    learning_applied: bool
    strategy_adaptation: Dict[str, Any]
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "autonomous_analysis": {
                    "resume_strength": 0.7,
                    "market_opportunity": 0.8,
                    "career_stage": "early_career",
                    "skill_gaps": ["advanced_ml", "leadership"],
                    "opportunities": ["skill_development_potential"],
                    "threats": ["skill_gaps"],
                    "recommended_focus": "balanced_improvement"
                },
                "agent_goals": ["network_building"],
                "identified_obstacles": ["skill_gaps", "limited_network"],
                "agent_actions": ["analyze_resume", "score_resume", "suggest_networking", "plan_skill_development", "track_progress"],
                "execution_results": {
                    "resume_and_job_matching": {
                        "resume_analysis": {
                            "strength_score": 0.7,
                            "skill_gaps": ["advanced_ml", "leadership"],
                            "opportunities": ["skill_development_potential"],
                            "threats": ["skill_gaps"],
                            "recommended_focus": "balanced_improvement"
                        },
                        "job_matching": {
                            "match_score": 0.85,
                            "insights": ["Strong technical background", "Consider adding leadership experience"],
                            "scoring_method": "ATS-style",
                            "confidence": "high"
                        },
                        "tailored_answers": {
                            "answers": [
                                {
                                    "question": "Why are you interested in this role?",
                                    "answer": "Tailored response based on resume and job requirements..."
                                }
                            ],
                            "overall_quality_score": 0.9,
                            "generation_method": "AI-tailored",
                            "confidence": "high"
                        }
                    },
                    "skill_development": {
                        "timeline": "3-6 months",
                        "skills_to_develop": ["advanced_ml", "leadership"],
                        "learning_resources": [
                            {
                                "skill": "advanced_ml",
                                "resources": ["Online course for advanced_ml", "Project in advanced_ml"],
                                "timeline": "2-3 months"
                            },
                            {
                                "skill": "leadership",
                                "resources": ["Online course for leadership", "Project in leadership"],
                                "timeline": "2-3 months"
                            }
                        ]
                    },
                    "career_development": {
                        "networking": [
                            {
                                "type": "professional_group",
                                "name": "ML Engineers Network",
                                "priority": "high"
                            }
                        ],
                        "progress": {
                            "status": "new_user",
                            "progress": 0
                        }
                    },
                    "agent_learning": {
                        "strategy_adaptation": {
                            "status": "initial_strategy",
                            "adaptations": 0
                        }
                    }
                },
                "learning_applied": True,
                "strategy_adaptation": {
                    "status": "initial_strategy",
                    "adaptations": 0
                }
            }
        }

@router.post("/autonomous-analysis", response_model=AutonomousAnalysisResponse)
async def autonomous_analysis_route(payload: AutonomousAnalysisRequest):
    """
    Truly agentic autonomous analysis that demonstrates:
    - Autonomous decision making
    - Goal-oriented behavior
    - Persistent memory and learning
    - Proactive problem solving
    - Strategy adaptation
    """
    try:
        print("🤖 Starting autonomous agentic analysis...")
        
        # Generate user ID if not provided
        user_id = payload.user_id or str(uuid.uuid4())
        
        # Convert job_posting_url to str if provided
        job_url = str(payload.job_posting_url) if payload.job_posting_url else None
        
        # Run the autonomous workflow
        result = await asyncio.to_thread(
            autonomous_career_workflow,
            user_id,
            payload.resume_text,
            job_url,
            payload.questions
        )
        
        print("✅ Autonomous analysis complete:", result)
        
        if result.get("success") is not False:
            return AutonomousAnalysisResponse(**result)
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Autonomous analysis failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        print(f"❌ Exception during autonomous analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-memory/{user_id}")
async def get_agent_memory(user_id: str):
    """
    Get the agent's memory and learning for a specific user
    """
    try:
        memory = true_agentic_agent.get_or_create_memory(user_id)
        
        return {
            "user_id": user_id,
            "total_interactions": len(memory.interactions),
            "total_outcomes": len(memory.outcomes),
            "strategies_used": len(memory.strategies),
            "goals_identified": [goal.value for goal in memory.goals],
            "created_at": memory.created_at.isoformat(),
            "last_updated": memory.last_updated.isoformat(),
            "recent_outcomes": memory.outcomes[-5:] if memory.outcomes else [],
            "current_strategies": memory.strategies[-3:] if memory.strategies else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-global-learning")
async def get_agent_global_learning():
    """
    Get the agent's global learning from all users
    """
    try:
        global_learning = true_agentic_agent.global_learning
        
        return {
            "total_users": len(true_agentic_agent.memories),
            "successful_strategies": len(global_learning["successful_strategies"]),
            "common_obstacles": list(set(global_learning["common_obstacles"])),
            "market_trends": global_learning["market_trends"],
            "skill_demands": global_learning["skill_demands"],
            "learning_summary": {
                "most_successful_strategy": _get_most_successful_strategy(global_learning),
                "most_common_obstacle": _get_most_common_obstacle(global_learning),
                "learning_effectiveness": len(global_learning["successful_strategies"]) / max(1, len(true_agentic_agent.memories))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-capabilities-autonomous")
async def get_autonomous_agent_capabilities():
    """
    Showcase the truly agentic capabilities
    """
    capabilities = {
        "agentic_features": {
            "autonomous_decision_making": {
                "description": "Agent makes decisions without being told what to do",
                "capabilities": [
                    "Analyzes situation independently",
                    "Identifies goals autonomously",
                    "Decides actions based on analysis",
                    "Executes actions proactively"
                ]
            },
            "goal_oriented_behavior": {
                "description": "Agent pursues specific career goals",
                "goals": [
                    "career_advancement",
                    "skill_development", 
                    "network_building",
                    "salary_improvement",
                    "work_life_balance"
                ]
            },
            "persistent_memory": {
                "description": "Agent remembers all interactions and learns over time",
                "memory_features": [
                    "User interaction history",
                    "Outcome tracking",
                    "Strategy effectiveness",
                    "Learning from failures",
                    "Adaptive behavior"
                ]
            },
            "proactive_problem_solving": {
                "description": "Agent identifies and solves problems before they become critical",
                "proactive_actions": [
                    "Detects skill gaps early",
                    "Identifies market opportunities",
                    "Suggests networking opportunities",
                    "Plans skill development",
                    "Tracks progress autonomously"
                ]
            },
            "strategy_adaptation": {
                "description": "Agent adapts strategies based on outcomes and learning",
                "adaptation_features": [
                    "Learns from successful strategies",
                    "Adapts to failures",
                    "Updates approach based on market changes",
                    "Personalizes strategies per user"
                ]
            }
        },
        "autonomous_workflow": {
            "step_1": "Agent analyzes current situation autonomously",
            "step_2": "Agent identifies goals and obstacles",
            "step_3": "Agent decides what actions to take",
            "step_4": "Agent executes actions proactively",
            "step_5": "Agent learns from outcomes",
            "step_6": "Agent adapts strategy for future"
        },
        "key_differences_from_traditional": {
            "traditional_tool": "Reactive - responds to user requests",
            "agentic_agent": "Proactive - takes initiative and makes decisions",
            "traditional_learning": "None - same response every time",
            "agentic_learning": "Continuous - improves with each interaction",
            "traditional_goals": "None - just processes requests",
            "agentic_goals": "Career advancement, skill development, networking",
            "traditional_memory": "None - stateless",
            "agentic_memory": "Persistent - remembers all interactions"
        }
    }
    
    return capabilities

def _get_most_successful_strategy(global_learning: Dict[str, Any]) -> str:
    """Helper to get most successful strategy"""
    strategies = global_learning.get("successful_strategies", [])
    if strategies:
        # Count strategy occurrences
        strategy_counts = {}
        for strategy in strategies:
            strategy_key = str(strategy.get("strategy", []))
            strategy_counts[strategy_key] = strategy_counts.get(strategy_key, 0) + 1
        
        # Return most common
        return max(strategy_counts.items(), key=lambda x: x[1])[0]
    return "No strategies yet"

def _get_most_common_obstacle(global_learning: Dict[str, Any]) -> str:
    """Helper to get most common obstacle"""
    obstacles = global_learning.get("common_obstacles", [])
    if obstacles:
        from collections import Counter
        return Counter(obstacles).most_common(1)[0][0]
    return "No obstacles identified yet" 
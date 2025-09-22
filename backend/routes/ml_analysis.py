from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
import os
import uuid
from pathlib import Path
import json
from typing import Dict, Optional

from ml.hybrid_analyzer import analyze_video_file, reset_analyzer, get_supported_exercises

router = APIRouter(prefix="/ml", tags=["ml-analysis"])

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

class AnalysisResult(BaseModel):
    video_id: str
    status: str
    results: Optional[Dict] = None
    error: Optional[str] = None

class VideoAnalysisRequest(BaseModel):
    video_id: str

# Store analysis results in memory (in production, use Redis or database)
analysis_results = {}

@router.post("/analyze-video", response_model=AnalysisResult)
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and analyze video for exercise counting"""
    
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    
    # Validate file type (be lenient for browsers that send octet-stream)
    file_extension = Path(file.filename).suffix.lower()
    allowed_ext = {'.webm', '.mp4', '.mov', '.mkv', '.avi'}
    content_type = (file.content_type or '').lower()
    if not (content_type.startswith('video/') or file_extension in allowed_ext):
        raise HTTPException(status_code=400, detail="File must be a video (.webm, .mp4, .mov, .mkv, .avi)")
    
    # Save uploaded file
    if not file_extension:
        file_extension = '.webm'
    video_path = UPLOADS_DIR / f"{video_id}{file_extension}"
    
    try:
        with open(video_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Start background analysis
        background_tasks.add_task(process_video_analysis, video_id, str(video_path))
        
        # Store initial result
        analysis_results[video_id] = {
            "video_id": video_id,
            "status": "processing",
            "results": None,
            "error": None
        }
        
        return AnalysisResult(
            video_id=video_id,
            status="processing"
        )
        
    except Exception as e:
        # Clean up file if analysis fails
        if video_path.exists():
            video_path.unlink()
        
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

@router.get("/analysis/{video_id}", response_model=AnalysisResult)
async def get_analysis_result(video_id: str):
    """Get analysis results for a video"""
    
    print(f"Getting analysis result for video {video_id}")
    print(f"Available results: {list(analysis_results.keys())}")
    
    if video_id not in analysis_results:
        print(f"Video {video_id} not found in results")
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[video_id]
    print(f"Returning result for video {video_id}: {result}")
    return AnalysisResult(**result)

@router.post("/reset-analyzer")
async def reset_analyzer_state():
    """Reset the exercise analyzer state"""
    reset_analyzer()
    return {"message": "Analyzer reset successfully"}

@router.get("/supported-exercises")
async def get_supported_exercises_endpoint():
    """Get list of supported exercise types"""
    exercises = get_supported_exercises()
    return {
        "exercises": exercises,
        "descriptions": {
            "pushup": "Push-up exercise counting and form analysis",
            "situp": "Sit-up exercise counting and form analysis", 
            "jump": "Jump exercise counting and form analysis"
        }
    }

async def process_video_analysis(video_id: str, video_path: str):
    """Background task to process video analysis"""
    try:
        print(f"Starting analysis for video {video_id}")
        
        # Analyze the video
        results = analyze_video_file(video_path)
        print(f"Analysis completed for video {video_id}: {results}")
        
        # Update results
        analysis_results[video_id] = {
            "video_id": video_id,
            "status": "completed",
            "results": results,
            "error": None
        }
        
        print(f"Results stored for video {video_id}")
        
        # Clean up video file after analysis
        if Path(video_path).exists():
            Path(video_path).unlink()
            print(f"Cleaned up video file: {video_path}")
        
    except Exception as e:
        print(f"Analysis failed for video {video_id}: {e}")
        
        # Update with error
        analysis_results[video_id] = {
            "video_id": video_id,
            "status": "failed",
            "results": None,
            "error": str(e)
        }
        
        # Clean up video file on error
        if Path(video_path).exists():
            Path(video_path).unlink()

@router.post("/analyze-frame")
async def analyze_single_frame(file: UploadFile = File(...)):
    """Analyze a single frame/image for pose detection"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Use hybrid analyzer for frame analysis
        from ..ml.hybrid_analyzer import analyzer
        
        # Process frame analysis
        result = analyzer.process_frame(None)
        
        return {
            "frame_analysis": result,
            "pose_detected": result["pose_detected"],
            "exercise": result["exercise"],
            "count": result["count"],
            "feedback": result["feedback"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze frame: {str(e)}")

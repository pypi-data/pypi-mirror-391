# Extracta - Simple Python Package First

## 🎯 Strategy: Python Package → Multiple Interfaces

**Core Principle**: Build `extracta` as pure Python package first, add UI layers later.

## 📦 Package Structure (Python First)

```
extracta/
├── extracta/
│   ├── __init__.py
│   ├── lenses/              # Content extraction
│   │   ├── __init__.py
│   │   ├── audio_lens/      # From deep-talk
│   │   ├── video_lens/      # Audio + visual
│   │   ├── code_lens/       # From existing code-lens
│   │   ├── document_lens/    # New implementation
│   │   └── base_lens.py     # Common interface
│   ├── analyzers/           # Content analysis
│   │   ├── __init__.py
│   │   ├── text_analyzer/    # New - critical
│   │   ├── image_analyzer/   # New - critical
│   │   ├── code_analyzer/    # Extract from code-lens
│   │   └── base_analyzer.py  # Common interface
│   ├── grading/             # Rubrics & scoring
│   │   ├── __init__.py
│   │   ├── grading_lens/     # New implementation
│   │   ├── rubric_manager/   # New implementation
│   │   └── feedback_generator.py
│   ├── orchestration/       # Workflow management
│   │   ├── __init__.py
│   │   ├── workflow_engine.py
│   │   └── content_router.py
│   └── shared/              # Common utilities
│       ├── __init__.py
│       ├── interfaces.py     # Base interfaces
│       ├── schemas.py       # Data models
│       ├── config.py        # Configuration
│       └── utils.py         # Helper functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Usage examples
├── pyproject.toml           # Package configuration
└── README.md               # Package documentation
```

## 🚀 Implementation Phases

### **Phase 1: Core Python Package (Weeks 1-12)**

#### **Weeks 1-2: Foundation**
```bash
# Create package structure
mkdir extracta
cd extracta
mkdir -p extracta/{lenses,analyzers,grading,orchestration,shared}
mkdir -p tests docs examples

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "extracta"
version = "0.1.0"
description = "Modular content analysis and insight generation"
authors = [{name = "Extracta Team"}]
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "click>=8.1.0",
    "pydantic>=2.5.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
audio = ["whisper-openai>=1.1.0", "librosa>=0.10.0"]
video = ["opencv-python>=4.8.0", "ffmpeg-python>=0.2.0"]
text = ["spacy>=3.7.0", "nltk>=3.8.0", "textstat>=0.7.0"]
image = ["pillow>=10.0.0", "torch>=2.0.0"]
code = ["radon>=6.0.0", "ruff>=0.1.0", "ast>=3.8"]
all = ["extracta[audio,video,text,image,code]"]

[project.scripts]
extracta = "extracta.cli:main"

[tool.ruff]
target-version = "py310"
line-length = 88
EOF
```

#### **Weeks 3-4: Migrate Existing Code**
```bash
# Migrate code-lens to extracta.lenses.code_lens
cp -r ../code-lens/codelens/* extracta/extracta/lenses/code_lens/

# Migrate deep-talk audio processing
cp -r ../deep-talk/src/services/* extracta/extracta/lenses/audio_lens/

# Update imports in migrated code
find extracta -name "*.py" -exec sed -i 's/from codelens/from extracta.lenses.code_lens/g' {} \;
find extracta -name "*.py" -exec sed -i 's/from services/from extracta.lenses.audio_lens/g' {} \;
```

#### **Weeks 5-8: Implement Missing Core**
```python
# extracta/extracta/analyzers/text_analyzer/__init__.py
from .analyzer import TextAnalyzer

# extracta/extracta/analyzers/text_analyzer/analyzer.py
class TextAnalyzer:
    """Research and assessment focused text analysis"""
    
    def analyze(self, text: str, mode: str = "assessment") -> dict:
        if mode == "research":
            return self._research_analysis(text)
        else:
            return self._assessment_analysis(text)
    
    def _research_analysis(self, text: str) -> dict:
        return {
            'themes': self._extract_themes(text),
            'discourse_patterns': self._analyze_discourse(text),
            'sentiment': self._analyze_sentiment(text),
            'linguistic_features': self._analyze_linguistics(text)
        }
    
    def _assessment_analysis(self, text: str) -> dict:
        return {
            'readability': self._analyze_readability(text),
            'writing_quality': self._analyze_quality(text),
            'vocabulary_richness': self._analyze_vocabulary(text),
            'grammar_issues': self._check_grammar(text)
        }
```

#### **Weeks 9-10: CLI Interface**
```python
# extracta/extracta/cli/__init__.py
from .main import main

# extracta/extracta/cli/main.py
import click
from pathlib import Path
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content

@click.group()
@click.version_option()
def main():
    """Extracta - Modular content analysis and insight generation"""
    pass

@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--mode', type=click.Choice(['research', 'assessment']), default='assessment')
@click.option('--output', '-o', type=click.Path())
def analyze(file_path, mode, output):
    """Analyze content from file"""
    file_path = Path(file_path)
    
    # Get appropriate lens
    lens = get_lens_for_file(file_path)
    if not lens:
        click.echo(f"No lens available for {file_path.suffix}", err=True)
        return
    
    click.echo(f"Analyzing {file_path.name}...")
    
    # Extract content
    result = lens.extract(file_path)
    if not result.success:
        click.echo(f"Error: {result.error}", err=True)
        return
    
    # Analyze content
    analyzer = get_analyzer_for_content(result.data['content_type'])
    if analyzer:
        analysis = analyzer.analyze(result.data['raw_content'], mode)
        result.data['analysis'] = analysis
    
    # Output results
    if output:
        import json
        with open(output, 'w') as f:
            json.dump(result.data, f, indent=2)
    else:
        click.echo(json.dumps(result.data, indent=2))
```

#### **Weeks 11-12: Testing & Documentation**
```python
# tests/test_text_analyzer.py
import pytest
from extracta.analyzers.text_analyzer import TextAnalyzer

class TestTextAnalyzer:
    def test_research_analysis(self):
        analyzer = TextAnalyzer()
        text = "This is a sample research interview transcript..."
        result = analyzer.analyze(text, mode="research")
        
        assert 'themes' in result
        assert 'discourse_patterns' in result
        assert 'sentiment' in result
    
    def test_assessment_analysis(self):
        analyzer = TextAnalyzer()
        text = "This is a student essay..."
        result = analyzer.analyze(text, mode="assessment")
        
        assert 'readability' in result
        assert 'writing_quality' in result
        assert 'vocabulary_richness' in result
```

### **Phase 2: Add API Layer (Weeks 13-14)**

#### **Weeks 13-14: FastAPI Server**
```python
# extracta/extracta/api/__init__.py
from .main import create_app

# extracta/extracta/api/main.py
from fastapi import FastAPI, UploadFile, File
from extracta.lenses import get_lens_for_file
from extracta.analyzers import get_analyzer_for_content

def create_app() -> FastAPI:
    app = FastAPI(
        title="Extracta API",
        description="Modular content analysis and insight generation",
        version="0.1.0"
    )
    
    @app.post("/extract")
    async def extract_content(file: UploadFile = File(...)):
        """Extract content from uploaded file"""
        # Same logic as CLI but via HTTP
        pass
    
    @app.post("/analyze")
    async def analyze_content(request: dict):
        """Analyze extracted content"""
        # Same logic as CLI but via HTTP
        pass
    
    return app

# Add to pyproject.toml
[project.optional-dependencies]
api = ["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0"]
```

### **Phase 3: Add GUI Layer (Weeks 15-16)**

#### **Weeks 15-16: React Frontend (Optional)**
```bash
# Create GUI directory
mkdir extracta/gui
cd extracta/gui

# Initialize React app (similar to assessment-bench)
npm create vite@latest . --template react-ts
```

## 🎯 Key Benefits of This Approach

### **1. Simplicity First**
- Focus on core Python functionality
- No UI complexity during initial development
- Clear testing and validation

### **2. Progressive Enhancement**
- Core package works standalone
- Add interfaces as needed
- Each interface optional

### **3. Multiple Consumption Patterns**
```bash
# CLI usage
extracta analyze interview.mp3 --mode research

# Python import
from extracta import TextAnalyzer
analyzer = TextAnalyzer()
result = analyzer.analyze(text, mode="research")

# API usage
curl -X POST "http://localhost:8000/extract" -F "file=@sample.mp3"

# GUI usage (later)
# React frontend calling same API
```

### **4. Easy Distribution**
```bash
# Install and test
pip install -e .
extracta --help

# Upload to PyPI
pip install extracta
extracta analyze document.pdf --mode assessment
```

## 📋 Implementation Checklist

### **Phase 1: Python Package (Weeks 1-12)**
- [ ] Create package structure
- [ ] Setup pyproject.toml
- [ ] Migrate existing code (code-lens, deep-talk)
- [ ] Implement text_analyzer (critical)
- [ ] Implement image_analyzer (critical)
- [ ] Create CLI interface
- [ ] Add comprehensive tests
- [ ] Write documentation

### **Phase 2: API Layer (Weeks 13-14)**
- [ ] Add FastAPI dependencies
- [ ] Create API endpoints
- [ ] Add authentication (optional)
- [ ] API documentation

### **Phase 3: GUI Layer (Weeks 15-16)**
- [ ] Create React frontend
- [ ] Connect to Python API
- [ ] Add desktop packaging (optional)

## 🚀 Getting Started

### **Immediate Actions**
```bash
# 1. Create package structure
mkdir extracta && cd extracta
# (See detailed setup commands above)

# 2. Migrate existing code
# (Copy from code-lens and deep-talk)

# 3. Install and test
pip install -e .
extracta --help

# 4. Start development
python -m extracta.cli analyze ../test-files/sample.mp3
```

This approach keeps things simple: build a solid Python package first, then add interfaces as needed.
# AI Quiz & Recommendation System

![AI Quiz System Banner](images/banner.png)

## Project Overview

The AI Quiz & Recommendation System is a sophisticated intelligent assessment platform that leverages advanced machine learning algorithms to provide personalized learning experiences. This comprehensive system evaluates user knowledge across multiple AI/ML domains, analyzes performance patterns, and generates tailored learning recommendations to optimize individual learning paths.

## Objective

The primary objective of the AI Quiz & Recommendation System is to revolutionize personalized learning by:
- Delivering adaptive assessments that adjust to individual learning patterns
- Providing comprehensive performance analytics with multi-dimensional scoring
- Generating personalized learning recommendations through machine learning algorithms
- Tracking progress over time to identify knowledge gaps and learning trends
- Creating an intuitive, responsive interface for seamless user interaction

## Demo & Documentation

- 📄 [Project Documentation](documentation.md)
- 🎥 [Video Preview](https://drive.google.com/file/d/1gBlS9XQ4CGe4Q7xfzRTcD_wuO-GikFAW/view)

## Setup Instructions

**a. Environment Setup**

1. **Clone the Repository:**
   ```
   git clone https://github.com/prathameshv07/AI_Quiz_System.git
   cd AI_Quiz_System
   ```

2. **Create and Activate Virtual Environment:**
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/macOS
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Initialize Database:**
   ```
   python -c "from core.database import init_database; init_database()"
   ```

**b. Optional Configuration** (Set Environment Variables)
   ```
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```

## Usage Guide

- Start the Streamlit server:
  ```
  streamlit run app.py
  ```
- The application will be available at `http://localhost:8501`

## Citation

If you use or build on this project, please cite it. GitHub's **"Cite this repository"** button (generated from [`CITATION.cff`](CITATION.cff)) provides APA and BibTeX formats.

```bibtex
@software{vaidya_aiquizsystem_2025,
  author = {Vaidya, Prathamesh Sarjerao},
  title  = {AI Quiz & Recommendation System},
  year   = {2025},
  url    = {https://github.com/Prathameshv07/AI_Quiz_System}
}
```

## License

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

© 2025 Prathamesh Sarjerao Vaidya. This work is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/). You may share and adapt it for **non-commercial** purposes, provided you **give appropriate credit** and indicate any changes. See [LICENSE](LICENSE) for details.

# Yoruba-sentiment-checker
Yorùbá Sentiment Checker
A hybrid (Rule-Based + Machine Learning) sentiment analysis tool for classifying Yorùbá text into Positive, Negative, or Neutral categories. This project addresses the challenge of building NLP tools for low-resource languages by combining the precision of a curated lexicon with the contextual understanding of a statistical model.

**Features**
Hybrid Architecture: Integrates a comprehensive, hand-curated Yorùbá sentiment lexicon with a Logistic Regression classifier for robust sentiment prediction.

**Web Application:** A user-friendly Streamlit web app for real-time sentiment analysis of text or uploaded files. https://yoruba-sentiment-checker.streamlit.app/

**Public Resources:** Provides a valuable public sentiment lexicon and sentiment analysis language model for Yorùbá to support further NLP research.

**Reproducible Research:** Complete code and methodology are provided for full transparency and reproducibility.

**Installation & Usage**

**Clone the repository:**

bash

git clone https://github.com/Kasaba6330/yoruba-sentiment-checker.git

cd yoruba-sentiment-checker

**Install dependencies:**

bash

pip install -r requirements.txt

**Run the web application:**

bash

streamlit run app.py

**Data**

The model is trained on an extended dataset built upon the Yorùbá portion of the AfriSenti-SemEval dataset.

**Contributing**

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

**License**

This project is licensed under the Apache-2.0 License.
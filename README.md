# PROJECT MUSEU NACIONAL - PRESENTATION DATA

**PROJECT MUSEU NACIONAL** is an interactive web application developed with **Streamlit** for visualization, exploration, and management of the Museu Nacional digital collection. The application allows researchers, students, and museum professionals to browse museum artifacts through an intuitive interface, providing access to metadata, images, statistical summaries, and advanced filtering capabilities.

The project aims to facilitate the analysis of museum collections while serving as a foundation for future research involving **Computer Vision**, **Large Vision-Language Models (LVLMs)**, **Image Classification**, **Image Retrieval**, and **Artificial Intelligence** applied to cultural heritage.

---

## Features 🚀

- Interactive dashboard developed with **Streamlit**
- Search artifacts by inventory number, object name, description, people, and metadata
- Dynamic filters for collection exploration
- Statistical overview of the dataset
- Individual artifact information page
- Image visualization (when available)
- Export filtered records to CSV
- Responsive and user-friendly interface

---

## Prerequisites 📋

Make sure you have the following software installed:

- Python 3.10 or later
- Pip (Python Package Manager)

### Python Libraries

- streamlit
- pandas
- numpy
- plotly
- pillow

---

## How to Run 🏃‍♀️

Follow these steps to configure and execute the application.

### 1. Clone the Repository

```bash
git clone https://github.com/your_username/ProjectMuseuNacional.git
```

### 2. Navigate to the Project Folder

```bash
cd ProjectMuseuNacional
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app_museu_nacional.py
```

The application will be available at:

```
http://localhost:8501
```

---

## Project Structure 📂

```text
ProjectMuseuNacional/
│
├── app_museu_nacional.py      # Streamlit application
├── BaseMN_003.csv             # Museum dataset
├── requirements.txt           # Python dependencies
├── images/                    # Artifact images (optional)
├── README.md
└── assets/                    # Additional resources
```

---

## Technologies Used 💻

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Pillow

---

## Future Improvements 🔬

The project is designed to support future developments involving Artificial Intelligence and Computer Vision, including:

- Image classification of museum artifacts
- Visual similarity search
- Semantic search using Large Language Models (LLMs)
- Vision-Language Models (VLMs)
- Automatic metadata generation
- Fine-tuning of multimodal models
- SQL database integration
- Authentication and user management
- REST API integration

---

## Contribution 🤝

Contributions are welcome!

If you would like to improve **Project Museu Nacional**, feel free to open issues or submit pull requests with new features, documentation improvements, or bug fixes.

---

## License 📄

This project is licensed under the **MIT License**. See the **LICENSE** file for more information.

---

## Acknowledgements 🙏

This project was developed as part of research on the digital preservation and intelligent analysis of the **Museu Nacional** collection.

Special thanks to everyone who contributed to the organization, cataloging, and availability of the museum data.

---

We hope **Project Museu Nacional** contributes to research in cultural heritage, digital humanities, and Artificial Intelligence. If you have any questions or suggestions, feel free to contact the development team.

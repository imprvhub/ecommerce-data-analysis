# Welcome to the [E-commerce Data Analysis](https://ecommerce-data-analysis.azurewebsites.net/) Project.
This implementation showcases and provides a comprehensive analysis of e-commerce data. Using Python (Flask Framework) with GUnicorn and Azure Deployment. For detailed insights, please visit [this link](https://ivanluna.dev/projects/post-python-ecommerce/).

### Live Demo:
https://ecommerce-data-analysis.azurewebsites.net/

### Key Features:
1. <ins>**Retrieve Data like a Super-Admin:**<ins>

   Obtain comprehensive data from store managers, including information about their stores, products, completed or pending sales, and customers.

2. <ins>**Comparative Rendering of Analytical Insights:**<ins>

   Render and compare the acquired data, providing analytical insights through tables, Plotly Express graphs, and Matplotlib visualizations.

3. <ins>**Dynamic Dashboard:**<ins>

   Access a dynamic dashboard that allows real-time monitoring and analysis of e-commerce metrics.

4. <ins>**User-Friendly Interface:**<ins>

   Navigate through a user-friendly interface designed for ease of use and efficient data exploration.
   
### Prerequisites:
[**Python 3.11**](https://www.python.org/downloads/release/python-3110/)

### Installation and Local Execution

#### 1. Clone 'Code With Antonio' Projects. 
In order to this implementation works properly you must to clone and set the [ecommerce-admin](https://github.com/antonioerdeljac/next13-ecommerce-admin) (in first place) and then [ecommerce-store](https://github.com/antonioerdeljac/next13-ecommerce-store) projects from 'Code With Antonio'. For detailed tutorial please visit: [Full Stack E-Commerce + Dashboard & CMS: Next.js 13 App Router, React, Tailwind, Prisma, MySQL, 2023](https://www.youtube.com/watch?v=5miHyP6lExg).

DISCLAIMER: Make sure to create a functional store from ecommerce-admin with products that can be viewed on the client side ecommerce-store. Keep in mind that the payments made in the demonstration are simulated and use generic data, following the recommended practices of [Stripe Docs](https://stripe.com/docs/testing ). If you have already configured payment management according to your region, then skip the simulation. It is recommended not to skip this step unless you are certain and take responsibility for the respective movements or transactions you generate. This project is purely demonstrative to showcase how a Python implementation works. We are not responsible for any misunderstandings or mismanagement. For more information: [Click here.](https://ecommerce-data-analysis.azurewebsites.net/user_agreements.html).

#### 2. Clone the implementation repository
```bash
git clone https://github.com/imprvhub/ecommerce_data_analysis.git
```
#### 2.1 Navigate to the project directory
```bash
cd /your/folder/directory/ecomerce-data-analysis
```
#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
#### 4. Start the application locally
```bash
python3 app.py
```
The application should now be accessible at http://localhost:8000.

### Conclusion:

#### Achievements

- **Successful Integration of Next.js Data:** Achieved the implementation of Python, effectively combining data extracted from two Next.js projects.

#### Learnings

- **Azure Deployment Debut:** This project marked my first deployment to Azure. While I had prior experience with Render, Vercel, and Netlify, configuring my Python application, powered by Gunicorn, to efficiently run on Azure presented a unique challenge.

#### Future Plans
- **Enhancing Performance Latency:** Occasionally, high Azure instance loads result in significant latency. To address this, I plan to migrate the project to a different platform in the future, thereby improving performance.
- **Interactive Enhancements:** In the future, I aspire to implement interactivity to the graphics and analytics, enhancing the overall user experience.

### Acknowledgments

- **Special Thanks to Code With Antonio:** Expressing my gratitude for inspiring with foundational projects and making this implementation possible.

### Feedback & Support
Your input matters, and I'm ready to help address any inquiries or feedback you may have. Your contributions are essential for refining the project and enhancing the overall user experience. Don't hesitate to get in touch with me:

Feel free to share your insights, recommendations, or suggestions for continuous improvement. If you encounter any challenges or require assistance, please [create a new GitHub issue](https://github.com/imprvhub/ecommerce-data-analysis/issues/new). Be sure to provide a detailed description of your issue to facilitate prompt and precise support.

### License
For more information regarding this topic please read the following [User Agreement Section.](https://ecommerce-data-analysis.azurewebsites.net/user_agreements.html)

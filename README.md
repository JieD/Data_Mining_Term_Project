# How to ask for a favor on line? - Data Mining Term Project
This is the term project for Data Mining course (CSc 869).

We are asking for something online all the time. We search for a specific information on ​Google​ or Facebook​. We turn to ​StackOverflow.com​ for programming solutions. I based my study on Random Acts of Pizza (ROAP), which is a ​reddit​ online community that is dedicated to give free pizza to strangers. I collected about 18,000 posts between June 2011 and April 2015. The success rate is around 12%, which is pretty low. So **what makes people satisfy certain requests over other requests online?**

The potential success factors can come from the following:
**1. Who is requesting?
2. How are they asking?
3. When are they asking?
4. What is being requested?**
The goal of this study is to understand the success factors and quantify their effects.

Description of the main strategy to realize the project:

1. Attribute Generation
The attribute generation phase in this project involves four major steps. They are raw ​reddit ​data collection, label generation, simple text analysis, and topic modeling.
  a. Raw Reddit Data Collection
I collected in total 37 preliminary attributes from reddit. They are mostly meta data of the request, like number of comments and upvotes.
  b. Label Generation
The data collected from reddit does not specify whether the request was successful (got_pizza) or unsuccessful (no_pizza). I used both the tag of a post and a human labeler to obtain the true label.
  c. Simple Text Analysis
With the obtained labels, I pulled together all the successful requests and observed some interesting patterns. For example, many successful requests provided images and stated they would reciprocate.
  d. Text Clustering
Based on the observation of the successful request, I used text clustering techniques to group similar requests together and extract the main topics. I processed the data and applied three techniques: K-Means, Non-Negative Matrix Factorization (NMF) and Latent Dirichlet Allocation (LDA) to extract the topics.

2. Classifier Construction
  In total, I selected 16 attributes (listed below) plus class label to feed to WEKA.
3. Evaluation results and discussions
  I chose four classifiers: Naive Bayesian, Logistic Regression, Decision Tree and Random Forest, and compared the result based on 10 fold cross-validation on oversampling dataset.
  Due to the dataset being highly skewed (only 12% success), I also applied oversampling and undersampling to offset the data imbalance.
  I used sklearn to construct learning curves and used WEKA GainRatio to rank the selected attributes.
  I also experimented with different combinations of attribute sets. The result shows that user information and topic modeling greatly increase the accuracy. In other words, the requester status and the request content play very important roles to success.
  Another interesting observation of the success count is that the earliest the request was made, the higher probability that it was satisfied.


Instructions on compiling and running my program:
  Programming Language: Python
  Development Environment: sqlite3, nltk, pandas, sklearn, gensim 
  Running Instructions:
  	1. Unzip the file.
  	2. Under the shell, run the following command:
  	   cd <the newly created directory>
  	   ./command

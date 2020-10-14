import pandas as pd
import numpy as np

path = r"data\automobiles.csv"
df = pd.read_csv(path)
df.describe(include='all')

## Data Pre-Processing

df.replace("?", np.nan, inplace = True) #replace the missing values("?") with nan
missing_data = df.isnull()
# this loop prints the number of missing values in each coloumn
for column in missing_data.columns.values.tolist():
    print(column)
    print (missing_data[column].value_counts())
    print("")

# replacing the missing values of some columns with their respective mean depending upon their type
avg_norm_loss = df["normalized-losses"].astype("float").mean(axis=0)
df["normalized-losses"].replace(np.nan, avg_norm_loss, inplace=True)

avg_bore = df["bore"].astype("float").mean(axis=0)
df["bore"].replace(np.nan, avg_bore, inplace=True)

avg_stroke = df["stroke"].astype("float").mean(axis=0)
df["stroke"].replace(np.nan, avg_stroke, inplace=True)

avg_horsepower = df["horsepower"].astype("float").mean(axis=0)
df["horsepower"].replace(np.nan, avg_horsepower, inplace=True)

avg_peakrpm = df["peak-rpm"].astype("float").mean(axis=0)
df["peak-rpm"].replace(np.nan, avg_peakrpm, inplace=True)

# replacing the missing values of columns with their respective frequency depending upon their type
max_freq=df["num-of-doors"].value_counts().idxmax()
df["num-of-doors"].replace(np.nan, max_freq, inplace=True) # replacing nan with value having maximum frequency in the coloumn

# droping the rows that do not have price values
df.dropna(subset=["price"], axis=0, inplace=True)
df.reset_index(drop=True, inplace=True)

# changing the data types of some columns to proper data types
df[["normalized-losses"]] = df[["normalized-losses"]].astype("int")
df["bore"] = df["bore"].astype("float")
df["stroke"] = df["stroke"].astype("float")
df["peak-rpm"] = df["peak-rpm"].astype("float")
df["price"] = df["price"].astype("float")
df["horsepower"]=df["horsepower"].astype("int")

## Data Analysis

df.corr()

# We now have a better idea of which variables are important to take into account when predicting the car price.
# We have narrowed it down to the following variables: Length, Width, Curb-weight, Engine-size, Horsepower, City-mpg, Highway-mpg, Wheel-base, Bore and Drive-wheels
# We can further verify this by calculating Pearson Correlation and performing ANOVA test.

from scipy import stats

#Pearson Correlation
pearson_coef, p_value = stats.pearsonr(df['wheel-base'], df['price'])
print("The Pearson Correlation Coefficient is between wheel-base and price is", pearson_coef, " with a P-value of P =", p_value)

pearson_coef, p_value = stats.pearsonr(df['horsepower'], df['price'])
print("The Pearson Correlation Coefficient between horsepower and price is", pearson_coef, " with a P-value of P = ", p_value)

pearson_coef, p_value = stats.pearsonr(df['length'], df['price'])
print("The Pearson Correlation Coefficient between length and price is", pearson_coef, " with a P-value of P = ", p_value)

pearson_coef, p_value = stats.pearsonr(df['width'], df['price'])
print("The Pearson Correlation Coefficient between width and price is", pearson_coef, " with a P-value of P =", p_value)

pearson_coef, p_value = stats.pearsonr(df['curb-weight'], df['price'])
print( "The Pearson Correlation Coefficient between curb-weight and price is", pearson_coef, " with a P-value of P = ", p_value)

pearson_coef, p_value = stats.pearsonr(df['engine-size'], df['price'])
print("The Pearson Correlation Coefficient between engine-size and price is", pearson_coef, " with a P-value of P =", p_value)

pearson_coef, p_value = stats.pearsonr(df['bore'], df['price'])
print("The Pearson Correlation Coefficient between bore and price is", pearson_coef, " with a P-value of P =  ", p_value)

pearson_coef, p_value = stats.pearsonr(df['city-mpg'], df['price'])
print("The Pearson Correlation Coefficient between city-mpg and price is", pearson_coef, " with a P-value of P = ", p_value)

pearson_coef, p_value = stats.pearsonr(df['highway-mpg'], df['price'])
print( "The Pearson Correlation Coefficient between highway-mpg and price is", pearson_coef, " with a P-value of P = ", p_value)

# ANOVA test for drive-wheels

grouped_test = df[['drive-wheels', 'price']].groupby(['drive-wheels'])

f_val, p_val = stats.f_oneway(grouped_test.get_group('fwd')['price'], grouped_test.get_group('rwd')['price'], grouped_test.get_group('4wd')['price'])
print( "ANOVA results: F=", f_val, ", P =", p_val)

## Model Development

from sklearn.linear_model import LinearRegression
lm = LinearRegression()

# Linear Regression
X = df[['horsepower']] # We can use other variables to preidict the price of car
Y = df['price']
lm.fit(X, Y)
Yhat_lr = lm.predict(X)
Yhat_lr[0:5]

# Multiple Linear Regression
Z = df[['horsepower', 'curb-weight', 'engine-size', 'highway-mpg']] # as these variables can be good predictor
lm.fit(Z, df['price'])
Yhat_mlr = lm.predict(Z)
Yhat_mlr[0:5]

# Polynomial Regression
from sklearn.preprocessing import PolynomialFeatures

pr = PolynomialFeatures(degree=2)
X_pr=pr.fit_transform(X)
lm.fit(X_pr, Y)
Yhat_pr = lm.predict(X_pr)
Yhat_pr[0:5]

# Model Evaluation using R-squared and Mean Squared Error(MSE)
from sklearn.metrics import mean_squared_error
# for linear regression
lm.fit(X, Y)
print('The R-square is: ', lm.score(X, Y))
mse = mean_squared_error(Y, Yhat_lr)
print('The mean square error of price and predicted value is: ', mse)

# for multiple linear regression
lm.fit(Z, Y)
print('The R-square is: ', lm.score(Z, Y))
mse = mean_squared_error(Y, Yhat_mlr)
print('The mean square error of price and predicted value is: ', mse)

# for polynomial regression
lm.fit(X_pr, Y)
print('The R-square is: ', lm.score(X_pr, Y))
mse = mean_squared_error(Y, Yhat_pr)
print('The mean square error of price and predicted value is: ', mse)

# When comparing models, the model with the higher R-squared value and smaller MSE value is a better fit for the data. In our case it is Multiple Linear Regression.

## Model Evaluation and Refinement

# Split the data into training and test data
from sklearn.model_selection import train_test_split
x_data = df.drop('price', axis=1)
y_data = df['price']
x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.45, random_state=0)

pr = PolynomialFeatures(degree=2)
x_train_pr=pr.fit_transform(x_train[['horsepower', 'curb-weight', 'engine-size', 'highway-mpg','wheel-base','bore']])
x_test_pr=pr.fit_transform(x_test[['horsepower', 'curb-weight', 'engine-size', 'highway-mpg','wheel-base','bore']])

# Ridge Regression

from sklearn.linear_model import Ridge

ridge_model = Ridge(alpha=0.1)
ridge_model.fit(x_train_pr, y_train)

yhat_ridge = ridge_model.predict(x_test_pr)

print('predicted:', yhat_ridge[0:4])
print('test set :', y_test[0:4].values)

print('The R-square is: ', ridge_model.score(x_test_pr, y_test))

# We can use Grid Search class to find the best hyperparameter alpha

from sklearn.model_selection import GridSearchCV

parameter = [{'alpha':[0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000]}]
RR = Ridge()
GS = GridSearchCV(RR, parameter, cv=4)
GS.fit(x_data[['horsepower', 'curb-weight', 'engine-size', 'highway-mpg','wheel-base','bore']], y_data)
BestRR=GS.best_estimator_
BestRR

# We now test our model using test data
BestRR.score(x_test[['horsepower', 'curb-weight', 'engine-size', 'highway-mpg','wheel-base','bore']], y_test)
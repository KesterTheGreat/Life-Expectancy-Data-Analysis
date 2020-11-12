
import pandas as pd
from pandas import DataFrame
import numpy as np
import os
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import warnings
from scipy import stats
import seaborn as sns
warnings.filterwarnings('ignore')

Lifeexp = pd.read_csv('E:\SCHOOL\CIND 820 PROJECT\Life Expectancy Data.csv', delimiter=',' ,dtype=None, index_col='Country')

Lifeexp.dataframeName= 'Life Expectancy Data.csv'

print(Lifeexp.head())
Lifeexp.rename(columns={"Life expectancy ":"Life_Exp",
                        "Adult Mortality":"A_Mortality",             
                        "infant deaths":"Infant_Deaths",
                        "percentage expenditure":"Pct_Exp",
                        "Hepatitis B":"HepatitisB",
                        "Measles ":"Measles",
                        " BMI ":"BMI","under-five deaths ":
                        "Under_Five_Deaths","Diphtheria ":"Diphtheria",
                        " HIV/AIDS":"HIV/AIDS",
                        " thinness  1-19 years":"thin_1-19",
                        " thinness 5-9 years":"thin_5-9",
                        "Income composition of resources":"Income_Comp_Of_Res",
                        "Total expenditure":"Total_Exp"},inplace=True)

# Get the data types
print(Lifeexp.dtypes)
# or to get more explanatory information
Lifeexp.info()



#Preliminary pruning of obvious outliers.

#Adult mortality rates lower than the 5th percentile
mortality_less_5_per = np.percentile(Lifeexp["A_Mortality"].dropna(),5) 
Lifeexp["A_Mortality"] = Lifeexp.apply(lambda x: np.nan if x["A_Mortality"] < mortality_less_5_per else x["A_Mortality"], axis=1)
#Remove Infant deaths of 0
Lifeexp["Infant_Deaths"] = Lifeexp["Infant_Deaths"].replace(0,np.nan)
#Remove the BMI less than 10 or greater than 50
Lifeexp["BMI"] =Lifeexp.apply(lambda x : np.nan if (x["BMI"] <10 or x["BMI"] >50) else x["BMI"],axis =1)
#Remove Under five deaths of 0
Lifeexp["Under_Five_Deaths"] =Lifeexp["Under_Five_Deaths"].replace(0,np.nan)



#Lets get the percentage of missing values in each column or variable
PctMissingValues = Lifeexp.isnull().sum()*100/Lifeexp.isnull().count()
print(PctMissingValues)

#Lets get the actual number of missing values in each column
No_of_MissingValues = Lifeexp.isnull().sum()  
print(No_of_MissingValues)


#Since almost half of the BMI column is now null. 
#I've decided to drop this variable completely
Lifeexp.drop(columns='BMI', inplace=True)



#Obtaining the number of unique values
unique_values = Lifeexp.nunique()
print(unique_values)



Lifeexp1 = []

for year in list(Lifeexp.Year.unique()):
    year_data = Lifeexp[Lifeexp.Year == year].copy()
    
    for col in list(year_data.columns)[2:]:
        year_data[col] = year_data[col].fillna(year_data[col].dropna().mode()[0]).copy()

    Lifeexp1.append(year_data)
Lifeexp1 = pd.concat(Lifeexp1).copy()

#Make sure missing values have been treated and filled
Lifeexp1.isnull().sum()
print(Lifeexp1)

No_of_MissingValues1 = Lifeexp1.isnull().sum()  
print(No_of_MissingValues1)

#Making a copy of the dataset which excludes 'Status' and 'year'
#This will be used for accurately counting the outliers and calculating the Z-scores
Lifeexp2 = Lifeexp1.drop(Lifeexp1.columns[[0,1]], axis=1)
print(Lifeexp2)


#OUTLIERS

#we'll use boxplots to show the distributions and detect outliers

#Creating a dictionary for the boxplot
lifeexp_dict = {'Life_Exp':1,'A_Mortality':2,
            'Infant_Deaths':3,'Alcohol':4,
            'Pct_Exp':5,'HepatitisB':6,'Measles':7,
            'Under_Five_Deaths':8,'Polio':9,
            'Total_Exp':10,'Diphtheria':11,'HIV/AIDS':12,
            'GDP':13,'Population':14,'thin_1-19':15,
            'thin_5-9':16,'Income_Comp_Of_Res':17,'Schooling':18}

# Detect outliers in each variable using box plots.
plt.figure(figsize=(20,30))

for variable,i in lifeexp_dict.items():
                     plt.subplot(5,7,i)
                     plt.boxplot(Lifeexp1[variable],whis=1.5)
                     plt.title(variable)
plt.show()           

#Histogram distributions
lifeexp_hist = ['Life_Exp','A_Mortality',
            'Infant_Deaths','Alcohol',
            'Pct_Exp','HepatitisB','Measles',
            'Under_Five_Deaths','Polio',
            'Total_Exp','Diphtheria','HIV/AIDS',
            'GDP','Population','thin_1-19',
            'thin_5-9','Income_Comp_Of_Res','Schooling']

plt.figure(figsize=(15,75))

for i in range(len(lifeexp_hist)):
    plt.subplot(18,5,i+1)
    plt.hist(Lifeexp1[lifeexp_hist[i]])
    plt.title(lifeexp_hist[i])

plt.show()

#--------------------------------------------------------------------

#Creating a fuction to find the amount and percentage of outliers in each variable

def no_of_outliers(col, data=Lifeexp1):
    
    print("\n"+15*'-' + col + 15*'-'+"\n")
    
    q75, q25 = np.percentile(data[col], [75, 25])
    iqr = q75 - q25
    min_val = q25 - (iqr*1.5)
    max_val = q75 + (iqr*1.5)
    no_of_outliers = len(np.where((data[col] > max_val) | (data[col] < min_val))[0])
    pct_of_outliers = round(no_of_outliers/len(data[col])*100, 2)
    print('Number of outliers: {}'.format(no_of_outliers))
    print('Percent of data that is outlier: {}%'.format(pct_of_outliers))
outlier_list = list(Lifeexp2)
for col in outlier_list:
    no_of_outliers(col)
    
#Descriptive statistics
print(Lifeexp2.describe())



#using 'Lifeexp2' dataset, we will calculate the Z-scores, 
#the z-cores over 3 or under -3 are outliers
cols = list(Lifeexp2.columns)
Lifeexp2[cols]
for col in cols:
    col_zscore = col + '_zscore'
    Lifeexp2[col_zscore] = (Lifeexp2[col] - Lifeexp2[col].mean())/Lifeexp2[col].std(ddof=0)
    print(Lifeexp2)



#Utilizing the winsorization method we will replace outliers.

from scipy.stats.mstats import winsorize

winsor_life_exp = winsorize(Lifeexp1['Life_Exp'],(0.01,0))
winsor_a_mortality = winsorize(Lifeexp1['A_Mortality'],(0,0.04))
winsor_infant_deaths = winsorize(Lifeexp1['Infant_Deaths'],(0,0.13))
winsor_Alcohol = winsorize(Lifeexp1['Alcohol'],(0,0.0025))
winsor_pct_exp = winsorize(Lifeexp1['Pct_Exp'],(0,0.135))
winsor_HepatitisB = winsorize(Lifeexp1['HepatitisB'],(0.11,0))
winsor_Measles = winsorize(Lifeexp1['Measles'],(0,0.19))
winsor_Under_Five_Deaths = winsorize(Lifeexp1['Under_Five_Deaths'],(0,0.15))
winsor_Polio = winsorize(Lifeexp1['Polio'],(0.1,0))
winsor_total_exp = winsorize(Lifeexp1['Total_Exp'],(0,0.02))
winsor_Diphtheria = winsorize(Lifeexp1['Diphtheria'],(0.105,0))
winsor_HIV = winsorize(Lifeexp1['HIV/AIDS'],(0,0.185))
winsor_GDP = winsorize(Lifeexp1['GDP'],(0,0.15))
winsor_Population = winsorize(Lifeexp1['Population'],(0,0.15))
winsor_thinness_1to19yrs = winsorize(Lifeexp1['thin_1-19'],(0,0.035))
winsor_thinness_5to9yrs = winsorize(Lifeexp1['thin_5-9'],(0,0.035))
winsor_Income_Comp_Of_Res = winsorize(Lifeexp1['Income_Comp_Of_Res'],(0.10,0))
winsor_Schooling = winsorize(Lifeexp1['Schooling'],(0.025,0.01))


Lifeexp1['winsor_life_exp'] = winsor_life_exp
Lifeexp1['winsor_a_mortality'] = winsor_a_mortality
Lifeexp1['winsor_infant_deaths'] = winsor_infant_deaths
Lifeexp1['winsor_Alcohol'] = winsor_Alcohol
Lifeexp1['winsor_pct_exp'] = winsor_pct_exp
Lifeexp1['winsor_HepatitisB'] = winsor_HepatitisB
Lifeexp1['winsor_Measles'] = winsor_Measles
Lifeexp1['winsor_Under_Five_Deaths'] = winsor_Under_Five_Deaths
Lifeexp1['winsor_Polio'] = winsor_Polio
Lifeexp1['winsor_total_exp'] = winsor_total_exp
Lifeexp1['winsor_Diphtheria'] = winsor_Diphtheria
Lifeexp1['winsor_HIV'] = winsor_HIV
Lifeexp1['winsor_GDP'] = winsor_GDP
Lifeexp1['winsor_Population'] = winsor_Population
Lifeexp1['winsor_thinness_1to19yrs'] = winsor_thinness_1to19yrs
Lifeexp1['winsor_thinness_5to9yrs'] = winsor_thinness_5to9yrs
Lifeexp1['winsor_Income_Comp_Of_Res'] = winsor_Income_Comp_Of_Res
Lifeexp1['winsor_Schooling'] = winsor_Schooling

print(Lifeexp1)



lifeexp_dict2 = {'winsor_life_exp':1,'winsor_a_mortality':2,
            'winsor_infant_deaths':3,'winsor_Alcohol':4,
            'winsor_pct_exp':5,'winsor_HepatitisB':6,'winsor_Measles':7, 
            'winsor_Under_Five_Deaths':9,'winsor_Polio':10,
            'winsor_total_exp':11,'winsor_Diphtheria':12,'winsor_HIV':13,
            'winsor_GDP':14,'winsor_Population':15,'winsor_thinness_1to19yrs':16,
            'winsor_thinness_5to9yrs':17,'winsor_Income_Comp_Of_Res':18,'winsor_Schooling':19}

# Detect outliers in each variable using box plots.
plt.figure(figsize=(15,75))

for variable,i in lifeexp_dict2.items():
                     plt.subplot(16,6,i)
                     plt.boxplot(Lifeexp1[variable],whis=1.5)
                     plt.title(variable)
plt.show()  


Lifeexp1.describe()



#Histogram distributions
lifeexp_hist2 = ['winsor_life_exp','winsor_a_mortality',
            'winsor_infant_deaths','winsor_Alcohol',
            'winsor_pct_exp','winsor_HepatitisB','winsor_Measles',  
            'winsor_Under_Five_Deaths','winsor_Polio',
            'winsor_total_exp','winsor_Diphtheria','winsor_HIV',
            'winsor_GDP','winsor_Population','winsor_thinness_1to19yrs',
            'winsor_thinness_5to9yrs','winsor_Income_Comp_Of_Res','winsor_Schooling']

plt.figure(figsize=(15,75))

for i in range(len(lifeexp_hist2)):
    plt.subplot(16,5,i+1)
    plt.hist(Lifeexp1[lifeexp_hist2[i]])
    plt.title(lifeexp_hist2[i])

plt.show()



# Descriptive statistics of categorical variables.
categ = Lifeexp1.describe(include=['O'])
print(categ)



winsor_life_exp = Lifeexp1[['Year','Status','winsor_life_exp','winsor_a_mortality',
            'winsor_infant_deaths','winsor_Alcohol',
            'winsor_pct_exp','winsor_HepatitisB','winsor_Measles',  
            'winsor_Under_Five_Deaths','winsor_Polio',
            'winsor_total_exp','winsor_Diphtheria','winsor_HIV',
            'winsor_GDP','winsor_Population','winsor_thinness_1to19yrs',
            'winsor_thinness_5to9yrs','winsor_Income_Comp_Of_Res','winsor_Schooling']]

print(winsor_life_exp)


# Using the winsorized dataset we will take a broad look a the rise in Life Expectancy from 2000 - 2015 using bar plot.
plt.figure(figsize=(8,6))
plt.bar(winsor_life_exp.groupby('Year')['Year'].count().index,
        winsor_life_exp.groupby('Year')['winsor_life_exp'].mean(),
        color='purple',alpha=0.80)
plt.xlabel("Year",fontsize=10)
plt.ylabel("Average Life Expectancy",fontsize=10)
plt.title("Life Expectancy through the years")
plt.show()


# create another barplot to give us a general idea of how life expectancy levels between developed and developing countries.
plt.figure(figsize=(8,6))
plt.bar(winsor_life_exp.groupby('Status')['Status'].count().index,
        winsor_life_exp.groupby('Status')['winsor_life_exp'].mean(),
        color= 'green',alpha=0.80)
plt.xlabel("Status",fontsize=12)
plt.ylabel("Average Life Expectancy",fontsize=12)
plt.title("Life Expectancy by country status")
plt.show()


# Life expectancy for each individual country
life_exp_country = winsor_life_exp.groupby('Country')['winsor_life_exp'].mean()
life_exp_country.plot(kind='bar', figsize=(50,15), fontsize=13)
plt.xlabel("Country",fontsize=35)
plt.ylabel("Average Life Expectancy",fontsize=35)
plt.title("Life Expectancy of each Country",fontsize=40)
plt.show()



#created a dataset which excludes the year, just for the heatmap
heat_life_exp = winsor_life_exp[['winsor_life_exp','winsor_a_mortality',
            'winsor_infant_deaths','winsor_Alcohol',
            'winsor_pct_exp','winsor_HepatitisB','winsor_Measles',  
            'winsor_Under_Five_Deaths','winsor_Polio',
            'winsor_total_exp','winsor_Diphtheria','winsor_HIV',
            'winsor_GDP','winsor_Population','winsor_thinness_1to19yrs',
            'winsor_thinness_5to9yrs','winsor_Income_Comp_Of_Res','winsor_Schooling']]

#created a function for heatmap of our dataset.
def life_exp_heatmap():
    plt.figure(figsize=(20,15))
    sns.heatmap(heat_life_exp.corr(), annot=True, fmt='.2g', vmin=-1, vmax=1, center=0, cmap='YlGnBu')
    plt.ylim(len(heat_life_exp.columns), 0)
    plt.title('Life Expectancy Correlation Matrix')
    plt.show()
life_exp_heatmap()


# Line plots showing the behaviours of Life Expectancy and Adult Mortality over the years

sns.lineplot('Year', 'winsor_life_exp', data=winsor_life_exp, marker='o')
plt.title('Life Expectancy by Year')
plt.show()

sns.lineplot('Year', 'winsor_a_mortality', data=winsor_life_exp, marker='o')
plt.title('Adult Mortality by Year')
plt.show()


#Scatter plots showing the relationship between Life expectancy and all continuous variables in our winsorized dataset.


plt.figure(figsize=(18,40))

plt.subplot(6,3,1)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_a_mortality"])
plt.title("Life Expectancy vs Adult Mortality")

plt.subplot(6,3,2)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_infant_deaths"])
plt.title("Life Expectancy vs Infant Deaths")

plt.subplot(6,3,3)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Alcohol"])
plt.title("Life Expectancy vs Alcohol")

plt.subplot(6,3,4)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_pct_exp"])
plt.title("Life Expectancy vs Percentage Exp")

plt.subplot(6,3,5)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_HepatitisB"])
plt.title("Life Expectancy vs HepatitisB")

plt.subplot(6,3,6)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Measles"])
plt.title("Life Expectancy vs Measles")

plt.subplot(6,3,7)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Under_Five_Deaths"])
plt.title("Life Expectancy vs Under Five Deaths")

plt.subplot(6,3,8)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Polio"])
plt.title("Life Expectancy vs Polio")

plt.subplot(6,3,9)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_total_exp"])
plt.title("Life Expectancy vs Total Expenditure")

plt.subplot(6,3,10)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Diphtheria"])
plt.title("Life Expectancy vs Diphtheria")

plt.subplot(6,3,11)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_HIV"])
plt.title("Life Expectancy vs HIV")

plt.subplot(6,3,12)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_GDP"])
plt.title("Life Expectancy vs GDP")

plt.subplot(6,3,13)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Population"])
plt.title("Life Expectancy vs Population")

plt.subplot(6,3,14)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_thinness_1to19yrs"])
plt.title("Life Expectancy vs thinness 1to19 years")

plt.subplot(6,3,15)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_thinness_5to9yrs"])
plt.title("Life Expectancy vs thinness 5to9 years")

plt.subplot(6,3,16)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Income_Comp_Of_Res"])
plt.title("Life Expectancy vs Income Comp Of Resources")

plt.subplot(6,3,17)
plt.scatter(winsor_life_exp["winsor_life_exp"], winsor_life_exp["winsor_Schooling"])
plt.title("Life Expectancy vs Schooling")


plt.show()



#Let us review a scatter plot showing the relationship between Income composition of resources and schooling.
plt.figure(figsize=(15,5))
plt.subplot(1,3,1)
plt.scatter(winsor_life_exp["winsor_Schooling"], winsor_life_exp["winsor_Income_Comp_Of_Res"])
plt.title("Schooling vs Income Comp Of Resources")
plt.show()













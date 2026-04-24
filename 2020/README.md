# Final Project PR Spring 2020

## Monte Carlo Simulation on Hospital Capacity during COVID-19


## Team Members- Rohit Sanvaliya, Tanya Gupta, Varad Deshpande

## The need for this project from the perspective of hospitals

COVID-19 came into this world without any warning or signs. This unannounced global pandemic was something the hospitals weren't prepared for and has called for crisis management measures. The hospitals have to make do with the available resources and make sure that there is maximum utilization of these resources to test and treat the patients that need urgent care. Our project witnesses a model called the SEIR model (Susceptible-Exposed-Infected-Result model) inspired from the SEIR model (Susceptible-Exposed-Infected-Recovered model). In our model, the R stands for result which includes people who are recovering as well as dying from COVID-19 compared to the R in the original SEIR model which stands for just the people who have recovered. Our model considers the various aspects of COVID-19, the statistics and data related to these aspects and then simulates the possibility of hospital beds overflowing for a fixed population and a fixed number of beds for a given number of days. This can prove to be helpful for hospitals in planning, managing and foreseeing the utilization of resources in these trying times enabling the healthworkers to drive their attention towards enhancing the diagnosis of the COVID-19 patients.


## Model for the simulation

SEIR model is a compartmental model where each compartment denotes the number of people in that compartment. 

The model is as follows: S --𝛽--> E --𝛼--> I --𝛾--> R

We have fit suitable variables in the model and altered the calculations for each transitional variable to get accurate results.

Susceptible (S): 100% of the population is Susceptible to COVID-19

Exposed (E): Number of people who have contracted the virus. We considered the social distancing and incubation rate (5%) of the Exposed

Infected (I): Total number of people that got infected

Result (R): Patients who have vacated the hospital bed either due to their recovery or death


## Simulation Variables

Infectious Rate (𝛽) = 𝑅_1* Outcome Rate (𝑅_1 – Reproduction Rate when social distancing is followed)

Incubation Rate (𝛼) = 1/Incubation Period (Incubation Period – The duration after which the patients show symptoms after being exposed)

Outcome (Result) Rate = 1/Infectious Period (Infectious Period – The duration in which the patient is capable of spreading COVID-19)

Arrival Rate of people to be tested – The rate at which potential infected people are arriving in the hospital

Probability of people testing positive for COVID-19 – Positive specimens out of the total specimens tested

Service time distribution of testing kits – The time taken to receive test results for COVID-19

Time to outcome (result) - It is the time taken by patients to either recover or for their unfortunate death


## Assumptions and Starting state for the Model

Fixed number of hospital beds

Fixed population around the hospital

Zero COVID-19 patients in the hospital initially

Hospital(s) can accommodate any arrival rate 

Social distancing is followed strictly

Testing kits used are 100% accurate (No false positive or false negative results)

Recovered patients are not getting re-infected


## Compartmental Equations

Each compartment in the our model gives the number of people in that compartment

Our inspired model has the following compartment definitions – 

Susceptible_𝑛 = Susceptible_(𝑛−1) - (𝛽 * Infected_(𝑛−1) * Susceptible_(𝑛−1))

Exposed_𝑛 = {Exposed_(𝑛−1) - (𝛼 * Exposed_(𝑛−1))} * 0.05  +++

Infected_𝑛 = (Arrival Rate of people to be tested * Probability of people testing positive for COVID-19 * Exposed_𝑛)

Hospitalized_𝑛 = 0.17 * Infected_𝑛  ++

Result_𝑛 = Outcome_Rate * Hospitalized_𝑛

+++ The value 0.05 is the probability that people will come in contact with each other despite social distancing

++ The value 0.17 is the probability of the total infected people being hospitalized


## Hypotheses

Our analysis is conducted on the Chicago area with population of 2.71 million and number of hospital beds being around 33000.

We have considered a fixed time period of 60 days for our simulation.

Using this, we ran 1000 simulations to test the hypothesis.

## Hypothesis-1

**If the number of hospital beds is doubled, there will never be an overflow.**


**Test-1**: Before doubling the number of beds

The following plot shows the simulation results depicting how beds in hospitals are occupied and how they will overflow after certain time.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h1b-beds-vs-days.png?raw=true "Available beds vs Days")


The following plot shows on which day the hospitals are most probable of overflowing.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h1b-overflow-days-hist.png?raw=true "Day on which the hospitals overflow")


**Test-2**: After Doubling the number of beds

The following plots shows the number of available beds once they are doubled. 

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h1F-beds-vs-days.png?raw=true "Available beds vs Days")


The following plot gives the available number of vacant beds in the hospitals and how they are not overflowing.

As the beds are not overflowing this graph shows no value for the nth day for the entire simulation.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h1F-overflow-days-hist.png?raw=true "Overflow day Hist")

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h1F-percent_vacant_beds-hist.png?raw=true "Percent Vacant Beds")

**Conclusion**: Hypothesis-1 is true. Thus, if the number of beds are doubled, there will never be an overflow for the given simulation.


## Hypothesis-2

**If 25% of the total population is strictly asked to follow a lockdown, 50% of the total hospital beds will become vacant.**


**Test-1**: Before the implementation of lockdown

The following plot shows the simulation results depicting how beds in hospitals are occupied and how they will overflow after certain time.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h2b-beds-vs-days.png?raw=true "Available beds vs Days")


The following plot shows on which day the hospitals are most probable of overflowing.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h2b-overflow-days-hist.png?raw=true "Day on which the hospitals overflow")


**Test-2**: After the implementation of lockdown

The following plot shows the simulation when the population was reduced by 25% then how the beds in hospitals are occupied and it shows that they do overflow.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h2F-beds-vs-days.png?raw=true "Available beds vs Days")

In the following plot we can see that percentage of vacant beds is zero for the entire simulation, i.e. there is an overflow

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h2F-percent_vacant_beds-hist.png?raw=true "Percent Vacant Beds Hist")

Finally, we see on which day hospitals are overflowing.

![Alt text](https://github.com/tanyagupta55/final_project_2020Sp/blob/master/Plots/h2F-overflow-days-hist.png?raw=true "Day on which the hospitals overflow")

**Conclusion**: Hypothesis-2 is false. As observed, if 25% of the total population is strictly asked to follow a lockdown, 50% of the total hospital beds will not become vacant. In fact, the beds are still seen overflowing.


## References:
https://www.datahubbs.com/social-distancing-to-slow-the-coronavirus/

https://www.vox.com/future-perfect/2020/4/15/21217027/coronavirus-social-distancing-flatten-curve-new-york

https://github.com/coronafighter/coronaSEIR/blob/master/main_coronaSEIR.py

https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus

https://www.medscape.com/answers/2500114-197431/what-is-the-incubation-period-for-coronavirus-disease-2019-covid-19

https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/05012020/covid-like-illness.html

https://www.inverse.com/mind-body/how-long-are-you-infectious-when-you-have-coronavirus

https://github.com/covid19-bh-biostats/seir/blob/master/SEIR/model_configs/basic

https://gis.cdc.gov/grasp/covidnet/COVID19_3.html

https://en.as.com/en/2020/04/12/other_sports/1586725810_541498.html

https://www.cdc.gov/coronavirus/2019-ncov/covid-data/covidview/index.html?CDC_AA_refVal=https%3A%2F%2Fwww.cdc.gov%2Fcoronavirus%2F2019-ncov%2Fcovid-data%2Fcovidview.html


## Work Distribution:
Varad contributed towards developing the model, coming up with the appropriate formulae and code development. Tanya helped in figuring out the distributions for each random variable, created meaningful visualizations for each hypothesis and enabled the efficient implementation of Travis CI. Rohit created sensible doctstrings and doctests for each function, added necessary comments in the code and optimized the speed of the overall code followed by implementation of Multiprocessing for the efficient and rapid execution of the simulations. Rohit and Tanya together ensured the addition of inline citations, looked after the intuitive naming of the variables and functions, and provided a clear structure to the code. The presentation was a collective effort of all the three members of the team.

### A1.pdf

**Citation**
- Chaupain-Guillot, S., & Guillot, O. (2015). Health system characteristics and unmet care needs in Europe: an analysis based on EU-SILC data. The European Journal of Health Economics, 16, 781-796. https://doi.org/10.1007/s10198-014-0629-x

**Data and setting**
- Data source: EU-SILC 2009 cross-sectional microdata.
- Time coverage: 2009 EU-SILC wave, with health-system contextual variables mainly referring to the late 2000s / 2008.
- Countries / population: EU-27 plus Norway and Iceland; 408,355 individuals aged 16+.
- Outcome definition: self-reported unmet need for medical examination/treatment and, separately, dental examination/treatment during the last 12 months. The dependent variable is coded 1 if the respondent reported at least one occasion when care was needed but not received, regardless of reason.
- Reasons for unmet need: EU-SILC reasons include cost, waiting list, lack of time, distance/transport, fear, "wait and see", not knowing a good provider, and other reasons. The authors also run an access-barrier version restricted to cost, waiting list, and distance/transport.

**Main research questions**
- The paper asks how much unmet medical and dental need varies across European countries and which individual, household, and health-system characteristics explain this variation.
- It gives special attention to health-system factors: physician/dentist density, access rules and gatekeeping, primary-care payment mode, and household out-of-pocket (OOP) payments as a share of total health expenditure.
- It explicitly tests whether country-level health-system characteristics explain residual between-country variation after accounting for individual socioeconomic and health characteristics.

**Methods**
- Two-level multilevel logistic regression, with individuals nested in countries.
- Separate models for medical and dental care.
- Level-1 covariates: sex, age, self-perceived health, citizenship, education, family situation, household income, housing tenure, non-housing debts, and car availability.
- Level-2 covariates: physicians/dentists per 100,000 inhabitants, access/gatekeeping rules, fee-for-service presence, and OOP share of total health expenditure.
- Additional random-coefficient models allow the income effect to vary across countries and test interactions between income quintiles and OOP share.
- Supplementary models restrict the outcome to access-barrier reasons: cost, waiting list, or distance/transport.

**Key findings (for unmet need / access / inequality)**
- In the full sample, 6.3% reported unmet medical need and 6.8% reported unmet dental need.
- Financial reasons accounted for about one-fourth of unmet medical need and about one-half of unmet dental need.
- Unmet need declines strongly with income: first-decile respondents had 10.8% unmet medical need and 12.0% unmet dental need, versus 3.9% and 3.4% in the top decile.
- Country rates vary sharply: Bulgaria and Latvia had rates above 15%, while Slovenia, Belgium, Luxembourg, and the Netherlands had rates below 2.5% for at least one care type.
- Worse self-rated health, low household income, rental housing, household debts, single parenthood, and no car are associated with higher unmet need.
- Older people report lower unmet need after adjustment, which the authors interpret as possibly reflecting greater tendency to seek care when needed.
- OOP share is the only health-system variable that is consistently significant: higher household OOP payments are associated with higher unmet medical and dental need.
- Physician/dentist density, access rules, gatekeeping, and fee-for-service payment are not significant at the national level. A 5 percentage-point increase in OOP share is associated with roughly a 0.8 percentage-point increase in unmet medical need and a 1.0 percentage-point increase in unmet dental need.

**Limitations**
- EU-SILC unmet need is self-reported and may vary with expectations, cultural norms, and perceived need across countries.
- Physician and dentist density are measured nationally, so regional provider shortages are not captured.
- The paper is mainly cross-sectional at the micro level; the authors note that unmet-need variables were not available in the Eurostat longitudinal EU-SILC files.
- Some health-system variables are coarse, especially the fee-for-service indicator and access-rule typologies.
- The analysis is associational; OOP, health-system design, and country socioeconomic context may be endogenous to broader welfare-state arrangements.

**Relevance for Mahdi's thesis**
- This is a core citation for using EU-SILC unmet medical need as a European access and inequality indicator.
- It directly supports including OOP share, income/poverty proxies, health-system capacity, and household financial strain as candidate predictors in a country-year panel.
- It provides an important prior: national physician/dentist density may be weak or nonsignificant at the country level, partly because within-country distribution is masked.
- Its multilevel logistic microdata design complements Mahdi's national-level panel/ML approach: it identifies individual-level gradients, while Mahdi can study country-year macro predictors and temporal validation.
- The paper explicitly warns that self-reported unmet need is not a causal health-system performance measure, matching Mahdi's predictive / associational framing.
- The access-barrier sensitivity outcome suggests Mahdi may want to distinguish "all reasons" from financial/availability reasons when working with hlth_silc_08 / 08b variants.

### A2.pdf

**Citation**
- Madureira-Lima, J., Reeves, A., Clair, A., & Stuckler, D. (2018). The Great Recession and inequalities in access to health care: a study of unemployment and unmet medical need in Europe in the economic crisis. International Journal of Epidemiology, 47(1), 58-68. https://doi.org/10.1093/ije/dyx193

**Data and setting**
- Data source: EU-SILC, combining information from cross-sectional and longitudinal arms to construct a pseudo-panel.
- Time coverage: 2008-2010, chosen to cover the early Great Recession period before later austerity measures changed policy conditions from 2011 onward.
- Countries / population: 25 European countries; analytical pseudo-panel n = 135,529. The sample is restricted to people who were employed and had no unmet medical need in the previous year.
- Outcome definition: unmet medical need, based on whether there was any time in the past 12 months when the respondent needed to consult a doctor or undertake medical examination/treatment but did not.
- Main exposure: transition from employment to unemployment.
- Contextual variables: household OOP payments as a percentage of total health expenditure from WHO Health for All, and income replacement for the unemployed (IRU) from Eurostat unemployment benefit expenditure divided by number of unemployed.

**Main research questions**
- The paper asks whether becoming unemployed during the Great Recession increased the probability of reporting unmet medical need.
- It investigates whether financial hardship mediates the job loss - unmet need relationship.
- It tests whether country-level financial protection through lower OOP payments or higher unemployment income replacement moderates the effect of job loss.

**Methods**
- Pseudo-panel construction links longitudinal employment information to cross-sectional unmet-need information using matching on predetermined characteristics.
- Linear probability models are the main specification, with random effects, fixed effects, and country random-coefficient robustness checks.
- Baseline sample design restricts attention to people employed in the previous year with met health needs, improving temporal ordering for job-loss transitions.
- Controls include age, sex, education, marital status, income quintile, ability to make ends meet, self-rated health, country dummies, and year dummies.
- Health-selection concerns are addressed with lagged health status, contemporaneous health, restricted samples with unchanged health, and fixed-effects checks.
- Moderation is tested by splitting countries around median OOP share and median IRU.

**Key findings (for unmet need / access / inequality)**
- The bivariate association indicates that job loss increased unmet medical need by 2.7 percentage points (95% CI 2.2-3.3).
- After demographic controls, becoming unemployed is associated with a 1.4 percentage-point higher probability of unmet medical need; after health controls the estimate remains about 1.1-1.2 percentage points.
- Financial hardship partially mediates the association: adding income and difficulty making ends meet attenuates the unemployment coefficient from 1.2 to 0.89 percentage points.
- The interaction between unemployment and difficulty making ends meet is important: unemployed people who lose the ability to make ends meet show about a 2.5 percentage-point increase in unmet need relative to those who do not.
- The job-loss effect is stronger in high-OOP countries: 2.5 percentage points in high-OOP countries versus 1.6 percentage points in low-OOP countries.
- Income gradients remain strong: lower income quintiles report higher unmet need, with the first income quintile showing the largest excess probability.
- Low IRU and poor health amplify vulnerability, although the paper reports a more nuanced moderation pattern for IRU than for OOP.
- The authors interpret unemployment as harmful for access mainly through declining financial resources, not through job loss alone.

**Limitations**
- The key outcome is not observed in the EU-SILC longitudinal file, requiring pseudo-panel matching rather than direct longitudinal observation of unmet need.
- Employment insecurity and precarious contracts are not measured, so access effects among insecurely employed people are omitted.
- National OOP measures do not capture exemptions, service-specific co-payments, or the difference between primary, specialist, emergency, and pharmaceutical costs.
- IRU is a country-year proxy based on aggregate spending per unemployed person, not an individual replacement rate.
- The results remain associational, despite careful temporal restrictions and robustness checks.

**Relevance for Mahdi's thesis**
- Strong support for including unemployment and financial hardship / poverty indicators as macro predictors of unmet medical need.
- Gives a theoretically clear mechanism for macroeconomic shocks: unemployment raises unmet need when household financial buffers weaken.
- Directly motivates interaction or nonlinear modeling around OOP and unemployment, which Mahdi's tree-based ensembles and regularised models can explore.
- Demonstrates the value of time-aware designs and pre/post-crisis framing, aligning with Mahdi's panel and temporal validation strategy.
- Shows how national OOP and social protection variables may moderate access inequality, even when the thesis remains predictive rather than causal.

### A3.pdf

**Citation**
- Israel, S. (2016). How social policies can improve financial accessibility of healthcare: a multi-level analysis of unmet medical need in European countries. International Journal for Equity in Health, 15, Article 41. https://doi.org/10.1186/s12939-016-0335-7

**Data and setting**
- Data source: EU-SILC 2012 microdata; macro policy variables are aggregated from EU-SILC beneficiary information, with OOP and physician density from WHO/OECD sources.
- Time coverage: main regression uses 2012; descriptive trend figure also discusses changes around 2009-2012.
- Countries / population: EU-28 plus Norway, Iceland, and Switzerland, excluding Croatia and Cyprus because of missing macro-level variables; 30 countries; 283,078 working-age individuals aged 18-65.
- Outcome definition: financial accessibility of healthcare (FAH), operationalised as "unmet need for medical examination or treatment" due to costs, transportation costs, or waiting lists. The author calls this broader category "enforced unmet medical needs".
- Target groups: whole working-age population and the first two income quintiles: Q1 as the lowest income quintile and Q2 as lower-middle income.

**Main research questions**
- The paper asks whether low-income groups face restricted financial accessibility to healthcare even under nominally universal European health systems.
- It studies whether social protection policies can supplement health policy by increasing disposable resources and reducing demand-side access barriers.
- It distinguishes whether the poorest quintile and lower-middle quintile face different barriers: indirect costs for Q1 versus direct financial stress, unemployment, and debt for Q2.

**Methods**
- Two-level multilevel logistic models with individuals nested in countries, estimated in Stata with adaptive Gaussian quadrature.
- Results are reported as average marginal effects, interpretable as percentage-point changes.
- Individual covariates include health status, chronic illness, sex, household composition, migrant status, education, urbanisation, access to public transport, access to primary healthcare, unemployment, debt/eviction risk, and log gross income.
- Macro covariates include OOP expenditure, physician density, unemployment benefits, family allowance, social allowance, and housing allowance.
- Models include a full population model and split models for Q1 and Q2.
- The author discusses Bonferroni correction and robustness checks using Eurostat expenditure data for social allowances.

**Key findings (for unmet need / access / inequality)**
- In 2012, cost was the most common reason for unmet medical need (36%), followed by waiting lists (15%); transportation accounted for about 3% among those reporting unmet need.
- Low FAH affected about 3% of the European population overall, but with large cross-country variation.
- Latvia, Romania, Poland, and Estonia had the highest proportions of low FAH; among the poor, the probability reached 22% in Latvia, 17% in Bulgaria, 14% in Romania, and about 11% in Italy, Greece, and Poland.
- After improvement up to 2009, access worsened again from 2010 onward, especially for the lowest quintile in Greece, Spain, Ireland, and Hungary.
- Individual risk factors include bad health, chronic illness, being a woman, single parenthood, migrant status, low education, unemployment, debt/eviction risk, low income, and worse access to primary care.
- For Q1, indirect access barriers matter more: public transport and primary-care accessibility have stronger effects among the poorest.
- For Q2, debt/eviction and unemployment are especially important, indicating vulnerability above the formal poverty line.
- Macro-level OOP is positively associated with low FAH, especially for Q2, while physician density is negatively associated with low FAH.
- Social allowance is the only social protection variable that is consistently significant; it reduces low FAH for both Q1 and Q2. Housing, family, and unemployment benefits are not statistically significant in the reported models.

**Limitations**
- EU-SILC cross-national income comparability is imperfect because sampling, survey modes, nonresponse imputation, and income reference periods vary across countries.
- The income components for benefits may rely on gross rather than net measures, which may distort cross-country ranking under different tax regimes.
- Unmet need is self-reported and requires respondents to perceive a medical need; low-health-knowledge groups may underreport unmet need.
- The broader FAH outcome combines cost, transport, and waiting lists; this captures realistic barriers but introduces subjectivity, especially for waiting time.
- The design is cross-sectional and cannot establish causal effects of social policy generosity on unmet need.

**Relevance for Mahdi's thesis**
- Strongly supports including social protection, poverty, unemployment, OOP, physician density, and access/capacity indicators in the covariate set.
- Shows that lower-middle groups may be vulnerable, not only the poorest; for national panels this motivates using inequality and poverty indicators rather than only GDP per capita.
- The distinction between direct costs, indirect costs, and availability barriers is useful for interpreting Eurostat unmet-need reason categories.
- The macro findings on OOP and physician density are directly relevant to Mahdi's health-system capacity and financing variables.
- It gives a policy-oriented explanation for why social expenditure indicators may improve prediction of unmet need in crisis and post-crisis years.
- It complements Mahdi's ML approach because the paper uses theory-driven multilevel logit models and average marginal effects, leaving room for predictive modeling of nonlinear interactions.

### A4.pdf

**Citation**
- Ramos, L. M., Quintal, C., Lourenco, O., & Antunes, M. (2019). Unmet needs across Europe: Disclosing knowledge beyond the ordinary measure. Health Policy, 123, 1155-1162. https://doi.org/10.1016/j.healthpol.2019.09.013

**Data and setting**
- Data source: European Social Survey (ESS), round 7, 2014, including the rotating module on Social Inequalities in Health.
- Time coverage: 2014 cross-section.
- Countries / population: European countries participating in ESS round 7; representative samples of persons aged 15+ in private households. The paper also studies the subgroup aged 65+.
- Outcome definition: subjective unmet needs (SUN) from the ESS question asking whether, in the last 12 months, the respondent was unable to get a medical consultation or treatment needed for listed reasons.
- Reasons include inability to pay, inability to take time off work, other commitments, treatment unavailable locally, waiting list too long, no appointments available, and other.
- The paper decomposes the ordinary prevalence measure: SUNw = prevalence of unmet needs in the whole population; SN = prevalence of people reporting medical care needs; SUNn = prevalence of unmet needs among those reporting need.

**Main research questions**
- The paper asks whether the usual indicator, unmet need as a share of the total population, hides important cross-country differences in the prevalence of need and the health system's ability to meet need.
- It proposes a decomposition framework for comparing countries with similar overall unmet-need prevalence but different need burdens.
- It examines how country rankings and health-system interpretations change when unmet need is measured among the population in need, including for older people.

**Methods**
- Descriptive cross-country measurement analysis using ESS sample weights.
- The central identity is SUNw = SN x SUNn.
- Countries are compared graphically using iso-SUNw curves, with SN on one axis and SUNn on the other.
- Analyses are presented for the full population aged 15+ and the subgroup aged 65+.
- The paper does not estimate multivariable regression models; it focuses on measurement, decomposition, and interpretation.

**Key findings (for unmet need / access / inequality)**
- The average SUNw across countries in 2014 is about 14.4% for the population aged 15+.
- The highest whole-population unmet-need prevalence appears in Poland (about 22%), Israel, France, and Portugal; Austria is below 6% and the Netherlands about 4%.
- Countries with the same SUNw can face different situations. Austria and Hungary both have about 6% SUNw, but Austria has high need prevalence and low unmet need among those in need, while Hungary has lower need prevalence and higher SUNn.
- Germany and Portugal have high need prevalence, whereas Poland and Israel have high unmet need among those in need.
- Sweden and Israel have similar need prevalence, but Israel's SUNn is much higher, implying worse access performance conditional on need.
- For the 65+ subgroup, need prevalence is generally higher, but unmet need among those in need is usually lower than in the whole population.
- Lithuania, Hungary, and the Czech Republic stand out because older people have both higher need prevalence and higher unmet need among those in need.
- The discussion notes that previous macro variables such as OOP and physician density show mixed evidence across studies, reinforcing the need to distinguish need burden from access failure.

**Limitations**
- ESS unmet need is self-reported and affected by expectations, social norms, cultural response patterns, and perceived health need.
- The ESS reasons differ from EU-SILC; for example, some "wait and see" behavior used in EU-SILC is not explicit in the ESS list.
- Small country samples limit reason-specific analysis by country.
- The paper is descriptive and cannot identify determinants of unmet need or establish causal mechanisms.
- Some reported needs may reflect social-care needs or dissatisfaction rather than clinically validated healthcare needs.

**Relevance for Mahdi's thesis**
- Important measurement citation: national unmet-need rates can mix two processes, population need prevalence and access conditional on need.
- This is directly relevant when interpreting Eurostat country-year indicators because a high rate may reflect high need burden, poor access, or both.
- It supports including demographic, health-status, and macro burden proxies where possible, not only health-system inputs.
- It offers a useful explanation for why GDP, ageing, poverty, and health-system capacity may interact in country-level prediction.
- It cautions against treating hlth_silc_08 as a pure health-system performance outcome; Mahdi can frame predictions as access/need associations.
- The decomposition idea can inform thesis discussion even if Mahdi's dataset only contains aggregate unmet-need rates.

### A5.pdf

**Citation**
- Cylus, J., & Papanicolas, I. (2015). An analysis of perceived access to health care in Europe: How universal is universal coverage? Health Policy, 119, 1133-1144. https://doi.org/10.1016/j.healthpol.2015.07.004

**Data and setting**
- Data source: European Social Survey (ESS), round 4, 2008.
- Time coverage: 2008 cross-section.
- Countries / population: 29 European countries; N = 51,835. Countries include EU members and non-EU countries such as Switzerland, Israel, Russia, Turkey, and Ukraine.
- Outcome definition: perceived future access to health care, based on whether respondents believed they would be able to access care if they needed it in the next 12 months. The binary outcome codes "not at all likely" or "not likely" as perceived inability to access care.
- The measure is not the same as realised past unmet medical need; it captures uncertainty about future access.
- Country-level contextual comparison: OOP expenditure as a share of total health expenditure from WHO Health for All.

**Main research questions**
- The paper asks how perceptions of access to health care vary across and within European countries with legal mandates for universal coverage.
- It identifies which individual socioeconomic and demographic characteristics are associated with perceived access barriers.
- It investigates whether low-income groups are uniquely disadvantaged within countries, or whether some systems create perceived barriers across income groups.

**Methods**
- Weighted logistic regressions with country fixed effects.
- Dependent variable: binary perceived inability to access care in the next 12 months.
- Individual covariates include self-rated health, income perception, education, age, employment volatility, sex, marital status, household size, citizenship, and current activity status.
- Robustness checks use income deciles instead of income perceptions and ordinal logistic regressions using all four access-response categories.
- Country-income interactions estimate country-specific access gaps between low-income and higher-income groups.
- Predicted probabilities are compared with OOP share of total health expenditure, but health-system characteristics are discussed contextually rather than formally modeled.

**Key findings (for unmet need / access / inequality)**
- Across the sample, 6.7% said it was very unlikely they could access care if needed, and another 18.5% said it was unlikely.
- Countries with the highest shares saying access was very unlikely included Ukraine (24.8%), Russia (19.7%), and Turkey (15.6%); Switzerland, Spain, and Sweden had the lowest.
- Low income, poor health, non-citizenship, being aged 20-30, unemployment, employment volatility, and being female are associated with higher odds of perceived access barriers.
- Income has a strong gradient: respondents finding it very difficult to get by have odds of perceived access barriers about 5.8 times those living comfortably.
- The country-level relationship between OOP share and perceived inability to access care is weakly positive but noisy.
- In Ukraine, Latvia, and Russia, access barriers are high for both high- and low-income respondents, suggesting quality, availability, rural accessibility, informal payments, or waiting times may matter beyond income.
- In some lower-barrier countries such as Belgium, France, Switzerland, and Cyprus, low-income groups still have much higher predicted probabilities of perceived access problems than high-income groups.
- The authors argue that OOP spending can be an imperfect indicator of access barriers because it is observed among users and may sometimes represent a way to bypass public-system barriers.

**Limitations**
- The outcome measures perceived future access, not actual unmet need or realised foregone care.
- Self-reported access, health, and income are subject to response-scale and cultural reporting biases; ESS has no anchoring vignettes.
- The access question appears only in the 2008 ESS round, preventing time-series analysis.
- The study cannot determine the precise reasons for perceived barriers; costs, provider availability, quality, waiting times, and informal payments may overlap.
- Country health-system features are not formally modeled because of typology complexity.

**Relevance for Mahdi's thesis**
- Useful for motivating why legal universal coverage does not eliminate access inequality in Europe.
- Supports inclusion of income/poverty, unemployment, health status proxies, citizenship/migration if available, and OOP measures when modeling unmet need.
- Provides a caution for Mahdi's macro data: OOP share may not monotonically capture barriers because high OOP can reflect both exclusion and private bypass routes.
- Highlights non-price rationing mechanisms such as waiting times, quality, and provider availability, which relate to hospital beds, physicians, and public expenditure variables.
- The paper complements EU-SILC studies by using ESS perceived access, helping Mahdi distinguish realised unmet need from broader access expectations.
- Its cross-sectional logistic design leaves a gap for Mahdi's panel and machine-learning approach to capture time-varying country-level patterns.

### A6.pdf

**Citation**
- Connolly, Sheelah, and Maev-Ann Wren (2017). Unmet healthcare needs in Ireland: Analysis using the EU-SILC survey. Health Policy. DOI: 10.1016/j.healthpol.2017.02.009.

**Data and setting**
- Data source: Irish component of EU-SILC 2013.
- Time coverage: 2013 cross-section, with contextual comparison to earlier Irish EU-SILC levels.
- Countries / population: Ireland; 12,663 individuals in 4,922 households, with the main analysis restricted to people aged 16 and over.
- Unmet need definition: self-reported unmet need for medical examination or treatment in the previous 12 months.
- Reasons captured: could not afford care, waiting list, could not take time, distance or transport, fear, waiting to see if problem improved, no good doctor or specialist available, and other reasons. The main reason analysis groups responses into cost, waiting, and other.

**Main research questions**
- The paper examines who reports unmet healthcare needs in Ireland and how reported reasons differ across socioeconomic, health, and insurance or eligibility groups.
- It studies whether Irish unmet need is mainly an affordability problem, a waiting-list problem, or a broader access problem.
- It places the results in the context of Ireland's mixed public-private system, where means-tested public entitlement and private insurance shape access.

**Methods**
- Binary logit model for the probability of reporting any unmet healthcare need.
- Multinomial logit model for the reason for unmet need, with cost, waiting list, and other reasons as alternatives.
- Level of analysis: individual-level cross-sectional survey analysis.
- Covariates include age, sex, income, education, employment, self-rated health, chronic illness, public eligibility category, and private insurance status.
- The authors use survey weights and robust standard errors clustered at household level; they also stratify some models by eligibility and insurance category because income affects both public entitlement and private insurance purchase.

**Key findings (for unmet need / access / inequality)**
- Overall reported unmet healthcare need was relatively low in Ireland in 2013 at 3.9%, but it had increased from 2.4% in 2004.
- Affordability was the dominant reason, accounting for about 59% of reported unmet need; waiting lists accounted for about 25%.
- Women, lower-income respondents, people in poorer health, and people with neither a medical/GP visit card nor private insurance were more likely to report unmet need.
- A clear income gradient remained after adjustment for demographic, health, and coverage variables.
- The income gradient was strongest among people without a medical/GP visit card and without private insurance, suggesting that partial coverage and OOP exposure matter.
- Respondents with only a medical card were more likely to cite waiting lists, while people with private insurance only or no card/insurance were more likely to cite cost.
- Younger respondents were more likely to cite affordability; older respondents were more likely to cite waiting lists.
- The findings suggest two different Irish access mechanisms: OOP payment barriers in primary and community care, and waiting barriers in the public acute hospital sector.

**Limitations**
- The outcome is self-reported and may be affected by recall, expectations, and perceptions of need.
- The measure misses clinically relevant unmet need that respondents do not perceive or report.
- Cross-sectional associations cannot identify causal effects of income, coverage, or health status.
- Health status may be both a cause and a consequence of unmet need, creating possible reverse causality.

**Relevance for Mahdi's thesis**
- This paper is highly relevant for distinguishing cost-related unmet need from waiting-list unmet need, which may respond to different macro and health-system covariates.
- It supports including OOP financing and coverage-related variables when explaining unmet medical need.
- It shows that national averages can be low while inequality by income and coverage remains important.
- Compared with Mahdi's country-year panel, the paper is micro-level and single-country, so Mahdi can position his thesis as complementing detailed Irish individual evidence with cross-national macro prediction.
- The paper strengthens the argument that unmet need is a health-system performance indicator, not only a demand-side preference measure.

### B1.pdf

**Citation**
- Elstad, Jon Ivar (2016). Income inequality and foregone medical care in Europe during The Great Recession: multilevel analyses of EU-SILC surveys 2008-2013. International Journal for Equity in Health. DOI: 10.1186/s12939-016-0389-6.

**Data and setting**
- Data source: EU-SILC microdata.
- Time coverage: 2008-2013.
- Countries / population: 30 European countries: all EU countries except Croatia, plus Iceland, Norway, and Switzerland; respondents aged 30-59; N = 1,242,361.
- Unmet need definition: "foregone medical care" due to costs, waiting lists, or travel difficulties, corresponding to enforced unmet medical care.
- The paper defines a disadvantaged group as people in the lowest national income tertile who also report chronic disease or fair/bad self-rated health.

**Main research questions**
- The paper asks whether foregone medical care increased during the Great Recession and whether increases were stronger among disadvantaged people.
- It examines whether country-level income inequality is associated with higher unmet care, independently of national income.
- It also tests whether GDP declines during the recession had larger access consequences in more unequal countries.

**Methods**
- Three-level multilevel linear probability models with individuals nested in country-years nested in countries.
- Models include individual controls for gender, age, education, unemployment, and rural residence.
- Country-level predictors include average real GDP per capita and income inequality measured by S80/S20.
- Country-year predictors include deviations in GDP and inequality from the country average, with GDP decline lagged approximately one year.
- The paper estimates separate models for disadvantaged respondents and all others, with random intercepts and selected random slopes.

**Key findings (for unmet need / access / inequality)**
- Foregone medical care increased in most countries between 2008 and 2013, especially among disadvantaged respondents.
- The unweighted country average among the disadvantaged increased from 8.3% in 2008/2009 to 10.1% in 2012/2013; among others it increased from 2.1% to 2.6%.
- Country variation was large: among disadvantaged respondents in 2012/2013, foregone care ranged from near zero in Slovenia to more than one third in Romania.
- Higher country-level income inequality was associated with more foregone care among disadvantaged respondents, net of GDP.
- GDP declines increased foregone care; in the main disadvantaged model, a 10% GDP decline predicted about a 1.5 percentage-point increase.
- The effect of GDP decline was stronger in more unequal countries, implying that macroeconomic shocks interact with distributional context.
- Among less disadvantaged respondents, GDP decline also mattered, but the estimated effect was smaller and inequality mainly operated through interaction with GDP decline.
- The results support the view that economic crisis and inequality can translate into unequal access to care even in European welfare states.

**Limitations**
- The outcome is self-reported and may underestimate access difficulty because severe cases may still obtain care despite barriers.
- EU-SILC measures perceived foregone care rather than clinically assessed unmet need.
- Country-level modelling is constrained by the small number of countries, limiting the number of macro predictors that can be included.
- The design is observational and cannot fully separate policy effects, macroeconomic shocks, and unobserved country characteristics.

**Relevance for Mahdi's thesis**
- This is one of the most directly relevant papers for Mahdi's macro-panel framing because it uses EU-SILC, European countries, time variation, GDP, and inequality.
- It supports including GDP per capita, unemployment or crisis-related variables, and inequality indicators such as S80/S20 or Gini.
- The interaction between GDP decline and inequality is a useful precedent for Mahdi to discuss nonlinearities and interaction effects that tree-based ML models may capture.
- The paper is explanatory multilevel modelling rather than predictive ML, so Mahdi can position his work as extending the same substantive question with regularised and nonlinear predictive models.
- Its disadvantaged-group focus helps motivate distribution-sensitive interpretation even when Mahdi's main outcome is national-level unmet need.

### B2.pdf

**Citation**
- Kaminska, Monika Ewa, and Melike Wulfgramm (2019). Universal or commodified healthcare? Linking out-of-pocket payments to income-related inequalities in unmet health needs in Europe. Journal of European Social Policy. DOI: 10.1177/0958928718774261.

**Data and setting**
- Data source: EU-SILC repeated cross-sections combined with OECD, World Bank, WHO, and Health Systems in Transition macro indicators.
- Time coverage: 2005-2012.
- Countries / population: 28 European countries; 179 country-year observations and 2,593,378 individual observations.
- Unmet need definition: unmet medical examination/treatment and unmet dental care are combined into a broader unmet health needs measure.
- Main outcome: unmet health need due to financial reasons, defined by reporting that care could not be afforded. Robustness analyses also consider all reasons and medical-only/dental-only outcomes.

**Main research questions**
- The paper asks whether higher out-of-pocket payments are linked to more income-related inequality in unmet health needs.
- It tests whether formally universal European systems can still generate commodified access through private payments.
- It examines whether OOP payments affect the overall level of unmet need and whether they steepen the income gradient.

**Methods**
- Three-level multilevel linear probability models with individuals nested in country-years nested in countries.
- Main individual predictor: equivalised disposable household income decile within each country-year.
- Main macro predictor: OOP payments as a percentage of total health expenditure.
- Key specification: cross-level interaction between individual income and national OOP share.
- Controls include health status, chronic illness, education, employment/economic status, household type, age, gender, GDP per capita, total health expenditure, Gini, gatekeeping, GP remuneration, and financing regime.
- Robustness checks include country fixed effects, a 2008 cross-section, medical-only and dental-only outcomes, all-reason unmet need, and alternative income-decile specifications.

**Key findings (for unmet need / access / inequality)**
- Income strongly predicts financially determined unmet health need across Europe.
- Higher OOP share is associated with higher financial unmet need and with steeper income-related inequality.
- At low OOP levels, the estimated poorest-richest gap is small; at high OOP levels, the gap becomes much larger, reaching double-digit percentage-point differences in high-OOP settings.
- The OOP-income interaction remains robust across country fixed effects and alternative outcome definitions.
- Total health expenditure, gatekeeping arrangements, GP remuneration, and NHS versus social insurance financing regime show less consistent associations.
- Bad health, chronic illness, unemployment, single parenthood, lower education, and female gender increase the risk of financially determined unmet need.
- The link between OOP payments and inequality is smaller but still visible when all reasons for unmet need are pooled.
- The paper's central conclusion is that universal coverage does not guarantee universal access when a high share of financing comes directly from households.

**Limitations**
- Unmet need is self-reported and may vary with cultural expectations and perceived need.
- The data are repeated cross-sections rather than individual panel data.
- Some macro data for non-OECD countries come from different international sources, creating possible measurement inconsistency.
- Health status may be endogenous to unmet need, although the authors test models with and without health controls.

**Relevance for Mahdi's thesis**
- This paper strongly supports including OOP share as a health-financing covariate in Mahdi's Eurostat models.
- It suggests that interactions between OOP share and poverty, income inequality, or low-income exposure may be substantively important.
- It motivates separating financial unmet need from aggregate unmet need where data allow, because OOP payments should be more predictive for affordability reasons than for waiting or distance.
- Compared with Mahdi's national-level predictive panel, this paper uses individual-level multilevel modelling; Mahdi can use it as micro evidence for macro feature selection.
- The results are a clear benchmark against which ML models can be interpreted: OOP financing should be expected to rank highly for financial unmet need.

### B3.pdf

**Citation**
- Carnazza, Giovanni, Paolo Liberati, and Giuliano Resce (2023). Income-related unmet needs in the European countries. Socio-Economic Planning Sciences. DOI: 10.1016/j.seps.2023.101542.

**Data and setting**
- Data source: European Health Interview Survey (EHIS), second wave.
- Time coverage: 2013-2015, with survey year varying by country.
- Countries / population: 29 European countries, including EU Member States plus Iceland and Norway; population aged 15 and over in private households.
- Unmet need definition: four EHIS access outcomes among people reporting a need for care: could not afford medical examination/treatment, could not afford prescribed medicines, long waiting lists, and distance/transport problems.
- The analysis focuses on people with perceived need, excluding those who report no need.

**Main research questions**
- The paper studies whether unmet healthcare needs are concentrated among lower-income groups across European countries.
- It asks whether different reasons for unmet need have different economic and institutional determinants.
- It evaluates whether country-level factors such as OOP spending, GDP, Gini, quality of government, and health expenditure are associated with both unmet need prevalence and income-related inequality.

**Methods**
- Inequality measurement uses the Erreygers Index for bounded binary outcomes, calculated with net equivalent household income.
- Country-level regressions relate unmet need prevalence and income-related inequality to standardized macro indicators.
- Individual-level logistic regressions estimate associations with age, gender, urban residence, marital status, education, unemployment, and above-median income.
- Outcomes are analysed separately for affordability of medical care, affordability of medicines, waiting lists, and distance/transport.

**Key findings (for unmet need / access / inequality)**
- In most countries, unmet needs are disproportionately concentrated among lower-income people.
- Income-related inequality is especially pronounced in countries such as Italy, Greece, and Latvia, while some systems show weaker or even reversed concentration for selected outcomes.
- Budget-constraint unmet needs, especially inability to afford medical care or prescribed medicines, are closely linked to economic variables and OOP spending.
- OOP share is associated with stronger low-income concentration of affordability-related unmet needs.
- Waiting-list and distance/transport inequalities appear more connected to institutional factors such as quality of government and health-system organization.
- At the individual level, higher income and male gender are generally protective across unmet-need categories.
- Unemployment increases the probability of all unmet-need categories; lower education and being unmarried also raise risk for most outcomes.
- Urban residence increases most unmet-need outcomes but reduces distance/transport unmet need, consistent with geographic access differences.

**Limitations**
- EHIS is cross-sectional, so associations should not be interpreted causally.
- The self-reported outcomes depend on perceived need, expectations, and national survey response patterns.
- Macro regressions are based on a limited number of countries and country-specific survey years.
- Excluding people who report no need focuses the analysis on access conditional on perceived need, not on total population burden.
- Some country-level variables are broad proxies and may not capture the exact health-system mechanisms behind waiting or distance barriers.

**Relevance for Mahdi's thesis**
- This paper provides strong support for analysing reasons for unmet need separately because affordability, waiting, and distance have different covariate profiles.
- It justifies including OOP share, GDP per capita, Gini, health expenditure, and institutional/capacity variables in Mahdi's macro feature set.
- Its use of inequality indices complements Mahdi's national-level prediction by giving an explicit income-distribution perspective.
- The distinction between economic drivers for affordability and institutional drivers for waiting/distance is useful for interpreting ML feature importance.
- Mahdi can position his Eurostat panel approach as extending this cross-sectional EHIS evidence over time with time-aware validation and predictive modelling.

### B4.pdf

**Citation**
- Fiorillo, Damiano (2020). Reasons for unmet needs for health care: the role of social capital and social support in some western EU countries. International Journal of Health Economics and Management. DOI: 10.1007/s10754-019-09271-0.

**Data and setting**
- Data source: EU-SILC 2006.
- Time coverage: 2006 cross-section.
- Countries / population: 14 western EU countries: Austria, Belgium, Germany, Denmark, Spain, Finland, France, Greece, Ireland, Italy, Netherlands, Portugal, Sweden, and the United Kingdom.
- Unmet need definition: self-reported unmet need for medical examination or treatment in the previous 12 months.
- Reasons analysed: expensive, no time, distance/transport, and wait-and-see. Other reasons are not modelled.

**Main research questions**
- The paper examines whether social capital and social support are associated with unmet healthcare needs and with specific reasons for unmet need.
- It asks whether family and friend networks reduce access barriers by helping people overcome cost, time, or distance constraints.
- The study focuses on western European countries with universal or near-universal coverage, where unmet need still persists.

**Methods**
- Two-step selection approach: a probit model first estimates the probability of any unmet need, then reason-specific probit models include a correction term.
- Social capital variables include daily contact with relatives, daily contact with friends, volunteering, and participation in organizations or groups.
- Social support is measured by the ability to ask relatives, friends, or neighbours for help.
- Controls include gender, age, marital status, household size, migrant status, education, log household income, home ownership, utility arrears, inability to handle unexpected expenses, employment status, health status, chronic conditions, activity limitations, municipality size, and country fixed effects.
- Selection variables include local noise, crime, and GPs per 1,000 inhabitants.

**Key findings (for unmet need / access / inequality)**
- About 7% of the sample reported unmet need; among those with unmet need, cost was the most common reason, followed by wait-and-see, time, and distance.
- Daily contact with relatives or friends and the ability to ask for help were negatively associated with any unmet need.
- Volunteering and participation in groups were positively associated with unmet need, possibly reflecting selection into social activity among people with health or access problems.
- Financial strain was strongly associated with unmet need: higher income and home ownership reduced risk, while utility arrears and inability to handle unexpected expenses increased risk.
- Poor health, chronic conditions, and activity limitations increased the probability of unmet need.
- Cost-related unmet need was more likely among women, larger households, lower-income respondents, people with financial constraints, unemployed people, and people in poor health.
- Social contact with friends and the ability to ask for help reduced cost-related unmet need, suggesting that informal support can partly buffer material barriers.
- Contact with relatives reduced time-constraint and distance-related reasons, while marital status lowered distance-related unmet need, consistent with practical support for access.

**Limitations**
- The analysis is cross-sectional and cannot establish causal effects of social capital or support.
- Social capital variables may be endogenous because health, unmet need, and social participation can influence each other.
- The exclusion restrictions in the selection approach may be contestable.
- EU-SILC 2006 is pre-crisis and does not capture later austerity, crisis, or post-crisis health-system changes.
- Results are limited to selected western EU countries and may not generalize to eastern or more recent European contexts.

**Relevance for Mahdi's thesis**
- This paper adds a demand-side and social-support perspective to Mahdi's more macro health-system and socioeconomic panel design.
- It confirms that income, financial strain, employment, and poor health remain important determinants even in universal systems.
- The reason-specific results reinforce the importance of distinguishing cost, time, distance, and waiting barriers when interpreting aggregate unmet need.
- Mahdi may not have social capital variables in Eurostat macro data, so this paper helps identify omitted individual-level mechanisms and residual heterogeneity.
- Its pre-crisis, cross-sectional design highlights a gap for Mahdi's time-aware, country-year predictive analysis.

### C1.pdf

**Citation**
- Moran, Valerie, Ellen Nolte, Marc Suhrcke, and Maria Ruiz-Castell (2025). Investigating the relationship between unmet need and utilisation of health care in European countries. Social Science & Medicine. DOI: 10.1016/j.socscimed.2025.117715.

**Data and setting**
- Data source: European Health Interview Survey (EHIS), wave 3, combined with Eurostat, OECD, World Bank, and OECD Health Systems Characteristics data.
- Time coverage: mainly 2019; Austria 2018-2019, Belgium 2018, and Germany/Malta 2019-2020; country characteristics mostly 2019 or latest available, with gatekeeping from 2016.
- Countries / population: 27 EU member states plus Iceland and Norway; 269,799 individuals aged 15+ living in private households.
- Unmet need definition: four binary EHIS outcomes among people reporting a need for care: unmet need due to long waiting list, distance/transport, inability to afford medical examination/treatment, and inability to afford prescribed medicines.
- Other access outcomes: GP consultation and specialist consultation in the previous 12 months.

**Main research questions**
- The paper asks how different dimensions of access relate to one another across European countries.
- It examines whether unmet need and utilisation measure the same access process or distinct dimensions of access.
- It also tests how individual socioeconomic, health, behavioural, and country-level health-system characteristics are associated with each access outcome.

**Methods**
- Multilevel multivariate random-effects logit models with individuals nested in countries.
- Six outcomes are modelled jointly: four unmet-need reasons plus GP and specialist utilisation.
- Individual predictors include age, sex, marital status, urbanisation, education, labour force status, household income, social support, smoking, self-rated health, multimorbidity, and activity limitation.
- Country predictors are modelled separately because the country sample is small: government/compulsory financing share, voluntary financing share, OOP share, health expenditure as % GDP, generalist and specialist physician density, gatekeeping, GDP per capita, and Gini.
- The authors estimate residual country-level variation and correlations between unexplained components of the access outcomes.

**Key findings (for unmet need / access / inequality)**
- At least one unmet need was highest in Luxembourg, Croatia, and Portugal; the most common reason in most countries was long waits, followed by affordability of medical care.
- Long-wait unmet need was especially high in Luxembourg, Iceland, and Portugal; affordability-related medical unmet need was highest in Latvia, Portugal, and Croatia.
- Poorer self-rated health, multimorbidity, and activity limitations were associated with both higher unmet need and higher utilisation.
- Higher household income was associated with lower unmet need and higher utilisation, especially specialist use.
- Country-level residual variation remained after individual adjustment, with about 8.6% of unexplained variation in long-wait and medical-affordability unmet need attributable to countries.
- Residual correlations among the four unmet-need measures were positive, but unmet need and utilisation had low individual-level correlations, implying that they measure different dimensions of access.
- At country level, unmet need due to unaffordable prescribed medicines was negatively correlated with GP and specialist utilisation.
- Higher government/compulsory financing share was associated with lower odds of unmet need due to affordability of medical care; higher Gini was associated with higher odds of medical-affordability unmet need.
- Gatekeeping was associated with lower specialist utilisation, while required gatekeeping was associated with higher odds of unmet need for prescribed medicines.

**Limitations**
- EHIS is cross-sectional and does not establish causality.
- Outcomes are self-reported and affected by country differences in expectations, survey mode, and response rates.
- EHIS unmet-need questions do not identify the exact service affected by long waits or distinguish GP from specialist affordability barriers.
- Country-level variables are coarse and can mask regional or local variation in physician supply and access.
- EHIS is collected infrequently, limiting time-series analysis compared with EU-SILC.

**Relevance for Mahdi's thesis**
- This is a strong conceptual and empirical complement to Mahdi's Eurostat work because it directly separates waiting, distance, medical affordability, and medicine affordability.
- It supports treating aggregate unmet medical need as only one dimension of access, not as a complete proxy for utilisation.
- The results justify Mahdi's inclusion of Gini, financing structure, OOP payments, physician density, GDP, and health expenditure variables.
- The weak link between utilisation and unmet need helps Mahdi explain why unmet need is an access/perceived-need outcome rather than a simple inverse of service use.
- The paper's cross-sectional EHIS design leaves space for Mahdi's annual Eurostat panel and time-aware prediction strategy.

### C2.pdf

**Citation**
- Detollenaere, Jens, Lise Hanssens, Veerle Vyncke, Jan De Maeseneer, and Sara Willems (2017). Do We Reap What We Sow? Exploring the Association between the Strength of European Primary Healthcare Systems and Inequity in Unmet Need. PLOS ONE. DOI: 10.1371/journal.pone.0169274.

**Data and setting**
- Data source: publicly available EU-SILC unmet-need statistics and Primary Healthcare Activity Monitor for Europe (PHAMEU) primary-care strength indicators.
- Time coverage: EU-SILC mainly 2013; older waves used where 2013 unmet-need data were unavailable; PHAMEU indicators from 2010.
- Countries / population: 31 European countries in the macro-level analysis.
- Unmet need definition: respondents reporting that in the last 12 months they needed medical examination or treatment but did not receive it.
- Inequality definition: country-level gap in unmet need between the lowest and highest equivalised-income quintiles.

**Main research questions**
- The paper asks whether stronger primary-care systems are associated with lower income-related inequity in unmet healthcare need.
- It examines whether specific primary-care dimensions, rather than primary care as a broad concept, are linked to access inequality.
- It also tests whether national income inequality, measured by Gini, is associated with the unmet-need gap.

**Methods**
- Macro-level ecological analysis using country-level aggregates.
- Primary-care strength is measured with seven PHAMEU dimensions: governance, economic conditions, workforce development, access, continuity, coordination, and comprehensiveness.
- Pearson correlations assess bivariate associations between primary-care strength and the unmet-need gap.
- Multiple linear regressions estimate associations between primary-care indicators and the income-related unmet-need gap, with a second model adding the Gini index.
- The dependent variable and governance indicator were log-transformed because of skewed distributions.

**Key findings (for unmet need / access / inequality)**
- The largest income-related unmet-need gap was found in Turkey; the Netherlands had the lowest gap.
- Higher national income inequality was associated with higher inequity in unmet healthcare need.
- After adjustment, the Gini coefficient remained significant: one standard deviation higher Gini was associated with a 4.960 higher unmet-need inequity score.
- Primary-care accessibility was inversely associated with the unmet-need gap; better PC access predicted lower inequality.
- Primary-care workforce development was also inversely associated with unmet-need inequity; one standard deviation higher workforce development was associated with a 4.951 lower inequity score.
- The access indicator and workforce development indicator remained significant after controlling for Gini.
- Other PC dimensions, including governance, economic conditions, continuity, coordination, and comprehensiveness, were not significantly associated with the unmet-need gap in the final model.
- The authors argue that reducing income inequality and strengthening accessible primary care are both relevant for reducing access inequity.

**Limitations**
- The design is ecological and macro-level, so individual-level mechanisms cannot be tested.
- The study is exploratory and limited by the small number of countries.
- EU-SILC self-reported unmet need is subjective and may reflect expectations as well as clinically grounded needs.
- Some countries required older EU-SILC waves, so country observations are not perfectly aligned in time.
- The unmet-need measure may include dental need in the public data used by the authors, which can overestimate the medical-care construct.

**Relevance for Mahdi's thesis**
- This paper directly supports Mahdi's use of health-system capacity and organisation variables, especially primary-care accessibility and workforce measures.
- It provides a clear precedent for using macro-level country indicators to explain inequality in unmet need.
- It reinforces the relevance of Gini and income inequality as covariates, not only poverty or GDP.
- Its macro ecological design is closer to Mahdi's national-panel design than most micro-level papers, although it is cross-sectional and non-ML.
- It gives Mahdi a useful caution: country-level models can identify system patterns but cannot prove the individual pathway from primary-care strength to unmet need.

### C3.pdf

**Citation**
- Kim, Tae Jun, Nico Vonneilich, Daniel Ludecke, and Olaf von dem Knesebeck (2017). Income, financial barriers to health care and public health expenditure: A multilevel analysis of 28 countries. Social Science & Medicine. DOI: 10.1016/j.socscimed.2017.01.044.

**Data and setting**
- Data source: International Social Survey Programme (ISSP) health and health care module, with World Bank, OECD Health Data, and Taiwan Ministry of Health and Welfare macro indicators.
- Time coverage: ISSP fieldwork mainly 2011, completed by 2013.
- Countries / population: 28 countries after excluding the Philippines as a total-health-expenditure outlier and excluding respondents with no need for treatment; final analytic sample 32,587 people, with multilevel models using 20,305 complete cases.
- The sample includes many European countries plus non-European comparators such as Australia, Chile, Israel, Japan, South Korea, South Africa, Taiwan, and the USA.
- Unmet need definition: forgone medical treatment in the past 12 months because the respondent could not pay for it; people reporting no need for treatment were excluded.

**Main research questions**
- The paper studies whether lower household income is associated with financial barriers to medical care across countries.
- It asks whether the strength of this income gradient varies with public health expenditure as a share of total health expenditure.
- It tests whether more public financing moderates income-related inequality in forgone care.

**Methods**
- Country-specific descriptive comparisons of forgone care by income tertile.
- Generalized linear mixed-effects logistic regression for binary outcomes, with country random intercepts.
- Individual predictors include income tertile, age, gender, education, subjective health, insurance coverage, and rural/urban residence.
- Macro predictors include public health expenditure as % total health expenditure and total health expenditure per capita.
- The authors test an interaction between income and public health expenditure to assess moderation.

**Key findings (for unmet need / access / inequality)**
- Overall, 9.1% of respondents who needed treatment reported forgone care because of inability to pay.
- Financial forgone care varied strongly by country, from 1.3% in Slovenia to 28% in Turkey.
- In 21 of 28 countries, lower income was significantly associated with higher financial forgone care.
- Across all countries, about 14% of the lowest income tertile reported forgone care compared with about 5% of the highest tertile.
- In multilevel models, the lowest income tertile had much higher odds of forgone care than the highest tertile; the adjusted OR was about 2.94.
- Poor subjective health, poor insurance coverage, female gender, urban residence, and low education were associated with higher odds of financial forgone care.
- Countries with public health expenditure between 60% and 80% of total health expenditure had higher odds of forgone care than countries above 80%, but the pattern was not straightforward.
- Public health expenditure did not significantly moderate the income-forgone-care relationship.

**Limitations**
- The outcome is self-reported and may not be comparable across cultures and survey contexts.
- Sampling procedures, survey modes, response rates, and sample sizes vary substantially by country.
- The study is cross-sectional and cannot identify causal effects of public spending.
- The public expenditure share is a broad financing measure and does not show where resources are spent or whether they reduce OOP exposure for low-income groups.
- The sample is not Europe-only, so direct transfer to Mahdi's European panel should be made cautiously.

**Relevance for Mahdi's thesis**
- This paper strengthens the case for income, poverty, insurance/coverage, and financing variables as predictors of financial unmet need.
- Its non-significant moderation finding warns that public expenditure share alone may be too crude; Mahdi may need OOP share, public expenditure, and capacity variables together.
- The possible nonlinear public-expenditure pattern supports Mahdi's use of tree-based and regularised models rather than relying only on linear effects.
- The paper is useful for discussing financial barriers, but it is less geographically aligned with Mahdi's Europe-only Eurostat thesis than EU-SILC/EHIS papers.
- It supports Mahdi's predictive framing: associations are strong but causal mechanisms remain uncertain.

### C4.pdf

**Citation**
- Reeves, Aaron, Martin McKee, Johan Mackenbach, Margaret Whitehead, and David Stuckler (2017). Public pensions and unmet medical need among older people: cross-national analysis of 16 European countries, 2004-2010. Journal of Epidemiology and Community Health. DOI: 10.1136/jech-2015-206257.

**Data and setting**
- Data source: Eurostat 2014 edition EU-SILC unmet-need data and the Comparative Welfare Entitlements Dataset (CWED), with Eurostat macroeconomic and health expenditure indicators.
- Time coverage: 2004-2010.
- Countries / population: 16 European countries: Austria, Belgium, Denmark, Finland, France, Germany, Greece, Ireland, Italy, Netherlands, Norway, Portugal, Spain, Sweden, Switzerland, and the UK.
- Unmet need definition: country-year prevalence of unmet medical need due to cost, based on EU-SILC self-reported unmet medical examination/treatment.
- Outcomes are disaggregated by age and income quintile; the main focus is people aged 65+.

**Main research questions**
- The paper asks whether more generous public pension entitlement reduces cost-related unmet medical need among older people.
- It tests whether pensions reduce income inequalities in unmet need across the older population.
- It also examines whether pension generosity matters more in systems with higher out-of-pocket payments.

**Methods**
- Country-level fixed-effects panel regressions using within-country changes over time.
- Main explanatory variable: public pension entitlement from CWED, based on replacement rates, duration, insurance years, contributions, and pension coverage.
- Controls include sickness entitlement, unemployment entitlement, GDP per capita, government health spending per capita, private pension expenditure, and chronic illness prevalence among older people.
- Robust standard errors are clustered by country.
- Sensitivity checks include time dummies, hospital beds, private pension measures, multilevel models, and falsification tests using unmet need for non-cost reasons.

**Key findings (for unmet need / access / inequality)**
- A one-unit increase in public pension entitlement was associated with a 1.11 percentage-point decline in cost-related unmet medical need among people aged 65+.
- The association was strongest for the lowest income quintile, with an estimated 1.65 percentage-point decline.
- Greater public pension entitlement appeared to reduce income inequalities in unmet need without worsening access among wealthier older people.
- OOP payments were linked to greater unmet need, but this association was mitigated by more generous public pension entitlement.
- The pension-unmet-need association was only observed in countries with high OOP expenditure, interpreted as more commodified health systems.
- Public pension entitlement was also negatively associated with cost-related unmet need among working-age people, but the effect was smaller.
- Sickness and unemployment entitlement were not clearly associated with unmet need among working-age people.
- Government health spending per capita was not clearly associated with unmet medical need in the working-age models.

**Limitations**
- The design uses ecological country-level pension indicators, so it cannot prove that individuals receiving higher pensions are the same people with lower unmet need.
- The country panel is small, although fixed effects and robustness checks improve credibility.
- Public pension entitlement is a composite indicator and does not isolate which policy component drives the association.
- The measure excludes much occupational pension variation.
- Self-reported unmet need may conflate needs and demands, although the authors adjust for chronic illness prevalence in older people.

**Relevance for Mahdi's thesis**
- This paper is directly relevant to Mahdi's country-year panel logic and use of Eurostat unmet-need outcomes.
- It supports including social protection or welfare-state variables where available, not only health-sector spending and capacity.
- The interaction between pensions and OOP expenditure is important for Mahdi's interpretation of nonlinearities and effect modification.
- It shows that health access inequalities can be shaped by income-support policy outside the health system.
- It provides a useful example of fixed-effects panel modelling and time-varying macro covariates, though the paper remains associational rather than causal proof.

### D1.pdf

**Citation**
- Doupe, Patrick, James Faghmous, and Sanjay Basu (2019). Machine Learning for Health Services Researchers. Value in Health. DOI: 10.1016/j.jval.2019.02.012.

**Data and setting**
- Data source: methodology primer, not an empirical unmet-need study.
- Demonstration data: simulated insurance claims dataset with 100,000 people.
- Outcome in the example: hospitalization for ambulatory care-sensitive conditions.
- Countries / population: no real country sample; the paper is written for health services researchers and decision makers.
- Unmet need definition: none; the paper contributes to modelling practice rather than access evidence.

**Main research questions**
- The paper explains how health services researchers should understand and apply machine learning for prediction tasks.
- It clarifies the workflow for developing estimators, selecting model families, regularising models, and evaluating generalisation.
- It compares regression, tree-based methods, deep learning, and ensembles for healthcare outcome prediction.

**Methods**
- Narrative methodological overview with applied examples in R and Python.
- Core workflow: data preparation, estimator family selection, parameter learning, regularisation, and estimator evaluation.
- Emphasises train/validation/test splits and K-fold cross-validation to reduce overfitting.
- Covers LASSO, ridge, and elastic net regularisation.
- Discusses decision trees, random forests, gradient boosting machines, neural networks, and stacked/meta-learner ensembles.
- Example performance metric: C-statistic/AUC, with discussion of calibration for healthcare decision contexts.

**Key findings (for unmet need / access / inequality)**
- The paper has no substantive findings on unmet need, access, or inequality.
- For predictive health services research, the prediction problem and success metric should be specified before model development.
- Held-out test evaluation is essential because high apparent fit on training data can reflect overfitting rather than generalisable prediction.
- Regularisation is central when many covariates are correlated, which is relevant for Mahdi's macro indicators such as GDP, poverty, unemployment, health expenditure, and OOP share.
- Tree ensembles and neural networks can capture nonlinearities and interactions, but they require stronger justification when interpretability matters.
- In the simulated example, gradient boosting had the highest C-statistic among the compared methods, while regularised logistic regression performed similarly to simpler logistic approaches.
- The authors stress that ML methods do not automatically outperform regression and should be matched to the research problem.
- Measurement quality matters: ML can accurately predict a biased or poorly measured outcome, which is relevant for self-reported unmet need.

**Limitations**
- The paper is a high-level primer rather than a systematic review or empirical health-access study.
- The applied example uses simulated claims data, not Eurostat, EU-SILC, EHIS, or panel data.
- It gives limited detail on time-aware validation, clustered/panel structures, or country-level small-N constraints.
- It discusses interpretability but not modern explainability tools in depth.
- It does not address fairness, health inequality metrics, or policy interpretation in detail.

**Relevance for Mahdi's thesis**
- This is useful for the thesis methods chapter because Mahdi uses regularised regression, tree-based ensembles, and neural-network surrogate models.
- It supports presenting Mahdi's models as predictive and associational, not causal.
- It justifies using held-out validation and careful metric selection, especially because time-aware validation is needed for country-year data.
- It gives language for explaining overfitting, regularisation, and the tradeoff between predictive performance and interpretability.
- Its warning about data quality is important for Eurostat self-reported unmet need: model performance does not remove measurement limitations.

### D2.pdf

**Citation**
Kino, Hsu, Shiba, Chien, Mita, Kawachi, and Daoud (2021). A scoping review on the use of machine learning in research on social determinants of health: Trends and research prospects. SSM - Population Health. DOI: 10.1016/j.ssmph.2021.100836.

**Data and setting**
- This is a scoping review of machine-learning applications in social determinants of health research, not an empirical unmet-need study.
- The authors searched before 1 May 2020, with no language or year restrictions, and followed PRISMA-ScR guidance.
- From 8097 initial records, 154 full texts were reviewed and 82 articles were included for data extraction.
- Included studies were mainly survey-based; more than half used US data, so the evidence base is not Europe-centred.
- The review groups applications into four themes: prediction, algorithmic fairness, causal inference, and data curation.
- Unmet medical need is not the outcome; the relevant setting for Mahdi is the broader use of ML to study social and health inequalities.

**Main research questions**
The paper asks how machine learning has been used in research on social determinants of health, what research themes dominate, and where future opportunities lie. It is especially interested in whether ML is used only for prediction or also for fairness analysis, causal inference support, and construction of new measures from non-traditional data. For Mahdi's thesis, the important contribution is methodological: it situates ML-based health inequality work within a broader social-determinants literature.

**Methods**
- Scoping review with structured search, title/abstract screening, full-text review, and two independent reviewers.
- Data charting covered research questions, datasets, algorithms, results, and the substantive theme of each paper.
- The review is descriptive and classificatory rather than a meta-analysis.
- It distinguishes routine predictive modelling from ML uses that address bias, measurement, or causal nuisance estimation.
- The level of analysis varies across included studies; the review itself does not estimate country-level or individual-level models.

**Key findings (for unmet need / access / inequality)**
- Most included studies used ML for ordinary prediction tasks rather than explicit inequality, fairness, or causal questions.
- Survey data still dominated the literature, despite ML's potential to use text, images, maps, accelerometer data, audio, and other unstructured sources.
- The authors argue that ML can reveal nonlinear associations and interactions among social determinants, which is relevant for macro covariates such as GDP, unemployment, poverty, Gini, health expenditure, OOP share, physicians, and beds.
- Algorithmic fairness receives limited attention in the reviewed literature, but the authors emphasise that prediction systems can reproduce or amplify social bias.
- ML alone cannot identify causal effects; causal interpretation still depends on research design and assumptions.
- ML can support causal inference when used to flexibly estimate nuisance functions, but only under credible identification assumptions.
- Data curation is a promising role for ML because it can turn unstructured or complex data into usable measures of social determinants.
- No direct evidence is provided on EU-SILC unmet medical need, waiting time, distance, or affordability barriers.

**Limitations**
- The review is broad and descriptive, so it does not provide pooled estimates or direct effect sizes.
- It is not focused on Europe, EU-SILC, healthcare access, or unmet medical need.
- Most included studies used US data and conventional surveys, limiting transferability to European country-year panels.
- The paper discusses causal inference conceptually but does not solve endogeneity or causal identification problems.
- Because it reviews heterogeneous studies, it is more useful for methodological framing than for covariate-specific evidence.

**Relevance for Mahdi's thesis**
- This is a useful methods/background citation for presenting Mahdi's work as applied ML for health-system inequality and social determinants of health.
- It supports using regularised regression, tree ensembles, and neural-network surrogates to model nonlinear associations among macro indicators.
- It also supports Mahdi's non-causal framing: good prediction or flexible modelling does not establish causal effects.
- The fairness discussion is relevant because national-level models of unmet need may encode structural inequality between countries and socioeconomic contexts.
- It helps justify why interpretable predictive modelling can complement, rather than replace, traditional panel regression.
- It is not a core empirical unmet-need paper, so it should be used mainly in the methods and motivation chapters.

### D3.pdf

**Citation**
Morgenstern, Buajitti, O'Neill, Piggott, Goel, Fridman, Kornas, and Rosella (2020). Predicting population health with machine learning: a scoping review. BMJ Open. DOI: 10.1136/bmjopen-2020-037860.

**Data and setting**
- This is a scoping review of machine-learning prediction studies in population health.
- Searches were run on 18 July 2018 across MEDLINE, EMBASE, CINAHL, ProQuest, Scopus, Web of Science, the Cochrane Library, INSPEC, ACM Digital Library, and grey-literature sources.
- Eligible studies were English-language articles from 1980-2018 using ML to predict population-health-related outcomes; studies using only logistic regression and primarily clinical contexts were excluded.
- The review included 231 articles from 22,618 records.
- The most common data sources were routine health records and population surveys.
- Unmet medical need is not the substantive outcome; the paper is relevant because Mahdi's thesis also uses predictive modelling for a population-health indicator.

**Main research questions**
The paper examines how machine learning has been used to predict population health outcomes and how well these studies report data, model development, validation, and performance. It asks whether the field is applying ML in a way that supports reliable population-health decision-making. For Mahdi, it provides a reporting and validation benchmark for ML models applied to national unmet-need data.

**Methods**
- Scoping review using the Arksey and O'Malley / Joanna Briggs approach and PRISMA-ScR reporting.
- Protocol was registered on OSF.
- Extraction categories were informed by ML predictive reporting guidance and TRIPOD.
- Extracted information covered study context, data source, sample size, number of features, algorithms, validation, discrimination, calibration, and authors' stated limitations.
- The review did not estimate new statistical models; it classified and summarised existing prediction studies.

**Key findings (for unmet need / access / inequality)**
- The most common study countries were the United States and China, so European population-health prediction studies were a minority.
- Median study size was 5414 observations and median feature count was 17, illustrating that many population-health ML applications are not extremely high-dimensional.
- Common algorithms included neural networks, support vector machines, single tree-based methods, and random forests.
- About half of studies compared ML models with statistical methods, usually logistic regression or ARIMA.
- Many papers gave weak reporting of hyperparameter selection, validation, or model-development procedures.
- Holdout validation was common, but external validation was rare, appearing in only a small share of studies.
- Discrimination metrics such as AUC and accuracy were commonly reported, while calibration was rarely assessed.
- Authors often discussed small samples, limited features, generalisability, and interpretability, but measurement error and selection bias were less frequently addressed.

**Limitations**
- This is a broad scoping review, not a review of unmet need, healthcare access, or health-system inequality.
- It includes English-language publications only and covers literature only through July 2018.
- The scope excludes several adjacent population-health tasks such as surveillance or health promotion if they were not prediction studies.
- It does not provide direct evidence about EU-SILC indicators or European macro covariates.
- The review's broad definition of population health makes the included studies heterogeneous.

**Relevance for Mahdi's thesis**
- The paper is a strong methodological citation for the ML part of Mahdi's thesis, especially model reporting, validation, and comparison with simpler statistical baselines.
- Its criticism of rare external validation supports Mahdi's use of time-aware validation for country-year panels.
- Its attention to calibration and generalisability is relevant when predicted unmet-need levels may be used for policy interpretation rather than only ranking countries.
- It supports discussing why nonlinear ML models may help, but also why they should not be assumed superior to panel regression or regularised regression.
- The under-discussion of measurement error is directly relevant to EU-SILC self-reported unmet need.
- It is not a source for substantive unmet-need covariates; it is primarily a methods and reporting reference.

### D4.pdf

**Citation**
Lee, Schwartz, Bansal, Khor, Hammarlund, Basu, and Devine (2022). A Scoping Review of the Use of Machine Learning in Health Economics and Outcomes Research: Part 2-Data From Nonwearables. Value in Health. DOI: 10.1016/j.jval.2022.07.011.

**Data and setting**
- This is a scoping review of machine-learning studies in health economics and outcomes research using nonwearable data.
- PubMed was searched for studies published from January 2020 through March 2021.
- The review was registered in PROSPERO as CRD42021260881.
- From 805 retrieved articles, the authors screened a random 20% sample for manageability and included 92 studies.
- Included studies used applied ML in HEOR settings; wearables, omics, imaging-only, non-HEOR, non-original, and methods-only studies were excluded.
- The review is not about unmet medical need, but it is close to Mahdi's thesis because it focuses on ML in health services, resource use, costs, and outcomes.

**Main research questions**
The paper asks how ML is being used in HEOR when data do not come from wearable devices. It describes the outcomes predicted, data sources used, algorithms selected, and model-testing practices. For Mahdi, it provides context for using ML in policy-relevant health-services research rather than purely clinical diagnosis.

**Methods**
- Scoping review with structured screening and abstraction.
- Extracted dimensions included ML application, data type, outcome type, training and testing data, algorithm, and performance metric.
- The review summarises counts and proportions, not pooled effects.
- Most included real-world-data studies were retrospective.
- Validation practices were abstracted, including use of independent test sets and cross-validation.

**Key findings (for unmet need / access / inequality)**
- ML in HEOR was mainly used for forecasting future outcomes rather than explaining current health-system inequality.
- Clinical events and treatment outcomes dominated; economic outcomes such as healthcare resource utilisation and costs were less common.
- Electronic medical records were the most common data source, followed by primary data; claims data were comparatively uncommon.
- Claims data were mostly used when the outcome was cost or healthcare resource utilisation.
- Tree-based models, including random forests and gradient boosting, were the most common algorithm family.
- Neural networks and support vector machines were also used, but logistic or linear regression remained common comparators or model choices.
- Some studies lacked an independent test set or did not clearly report model testing, reinforcing the need for transparent validation.
- The paper identifies an evidence gap around ML for economic and resource-use outcomes, which is adjacent to unmet need and health-system capacity.

**Limitations**
- The review covers a short publication window, January 2020 to March 2021, and may reflect COVID-era publication patterns.
- It uses a random 20% sample of retrieved records, so some relevant studies were not reviewed.
- It is limited to PubMed and English-language articles.
- It does not focus on Europe, national panels, Eurostat, EU-SILC, or unmet medical need.
- It is descriptive and cannot assess whether ML improved policy decisions or reduced inequality.

**Relevance for Mahdi's thesis**
- This paper supports placing Mahdi's work within HEOR-oriented ML rather than only generic data science.
- It justifies comparing regularised regression with tree-based ensembles and neural-network approaches.
- Its finding that economic/resource-use outcomes are underrepresented helps Mahdi frame unmet need and system-capacity prediction as a useful gap.
- It reinforces the need to report training/testing strategy, performance metrics, and validation design clearly.
- It is useful for the methods chapter, but not for substantive estimates of poverty, unemployment, Gini, OOP share, physicians, or beds.

### E1.pdf

**Citation**
Ranjan, Thiagarajan, Shanmugam, and Garg (2023). Measurement of unmet healthcare needs to assess progress on universal health coverage - exploring a novel approach based on household surveys. BMC Health Services Research. DOI: 10.1186/s12913-023-09542-0.

**Data and setting**
- Cross-sectional household survey in Korba district, Chhattisgarh, India.
- The survey used multistage random sampling and covered 598 households and 3153 individuals.
- The setting was a district where residents were formally covered by government-funded insurance for many secondary and tertiary services and by a public three-tier health system.
- The paper measured perceived need for acute and chronic illness, incomplete care, use of unqualified providers, and latent/unperceived need through tracer conditions.
- Latent need was assessed for hypertension, diabetes, and depression.
- This is not an EU-SILC or European paper, but it is directly about how unmet healthcare need should be measured.

**Main research questions**
The paper asks whether household surveys can measure unmet healthcare needs more comprehensively than standard utilisation or insurance-coverage indicators. It argues that universal health coverage monitoring should include perceived unmet need, incomplete care, inappropriate care, and latent needs that respondents may not recognise. For Mahdi, it is especially relevant to the interpretation and limitation of self-reported unmet medical need indicators.

**Methods**
- Cross-sectional household survey with multistage random sampling.
- Villages and urban wards were selected using probability proportional to size, followed by household selection within sampled areas.
- Data collection combined self-reported healthcare needs and utilisation with clinical screening or measurement for selected tracer conditions.
- The analysis is descriptive, comparing reported illness, treatment seeking, provider type, medication continuity, and undetected conditions.
- The unit of analysis is households and individuals, not regions or country-years.

**Key findings (for unmet need / access / inequality)**
- A standard one-line unmet-need question can substantially underestimate healthcare need because it captures only perceived and reported barriers.
- Among people reporting acute ailments, a notable share received no treatment, and many others received care from unqualified providers.
- Among people reporting chronic conditions, some received no treatment and many received incomplete medication coverage across the year.
- The study found substantial latent need: many adults had never had blood pressure measured.
- Most people identified as likely to have depression had not sought care and did not know they might have depression.
- The authors argue that perceived need can be higher among less marginalised groups because awareness, diagnosis, and expectations differ by socioeconomic position.
- Including latent need changes the equity interpretation, showing that poorer or marginalised groups may have larger unmet need than self-report alone suggests.
- The paper links unmet need not only to affordability but also to service availability, primary-care scope, and quality of care.

**Limitations**
- The study is based on one district in India and is not representative of India or Europe.
- It is cross-sectional and does not capture seasonality or temporal dynamics.
- Latent need is measured only for three tracer conditions, so total latent need is likely broader than the study can measure.
- Inappropriate care is difficult to measure quantitatively and may require qualitative follow-up.
- The study does not estimate panel models or causal effects.

**Relevance for Mahdi's thesis**
- This is a useful measurement-limitations citation: EU-SILC hlth_silc_08/08b measures self-reported perceived unmet need, not latent clinical need.
- It supports caution that low reported unmet need in some countries or groups may reflect lower expectations, lower diagnosis, or lower awareness rather than true absence of need.
- It helps Mahdi discuss why self-reported access indicators are policy-relevant but incomplete.
- It suggests that socioeconomic covariates such as poverty, education, unemployment, and income inequality may affect both actual access and recognition/reporting of need.
- It is not directly comparable to Mahdi's Europe-level panel, so it should be used mainly in the conceptual and limitations sections.

### Rare disease care in Europe – Gaping unmet needs.pdf

**Citation**
Pakter (2024). Rare disease care in Europe - Gaping unmet needs. Rare. DOI: 10.1016/j.rare.2024.100018.

**Data and setting**
- This is a European legal and health-policy article, not an empirical statistical study.
- The setting is rare disease care in Europe and the European Union.
- The paper draws on EU regulations and directives, European Commission evaluations, EURORDIS material, the IQVIA WAIT indicator, and legal/policy sources.
- It discusses the EU Orphan Medicinal Products Regulation, Regulation (EC) No 883/2004 on social-security coordination, and the 2011 Cross-border Healthcare Directive.
- Unmet need is conceptualised as absence of effective treatment, unequal availability of orphan medicinal products, reimbursement barriers, high prices, and difficulty using cross-border care.
- It does not use EU-SILC and does not measure self-reported unmet need for medical examination.

**Main research questions**
The article asks why rare disease patients in Europe still face large unmet needs despite strong European social protection and EU-level orphan-drug regulation. It focuses on treatment development, orphan-drug access, reimbursement, cross-border healthcare rights, and differences between Member States. For Mahdi, it provides a policy example of how European health-system inequality can persist even when formal legal and regulatory frameworks exist.

**Methods**
- Narrative legal and policy analysis.
- The article synthesises secondary evidence from EU legal instruments, policy evaluations, patient-organisation reports, and access indicators.
- There is no regression modelling, survey analysis, or country-year panel dataset.
- The level of analysis is EU policy and Member-State access variation.
- The article is advocacy-oriented and argues for reform of the EU orphan-drug framework and cross-border access arrangements.

**Key findings (for unmet need / access / inequality)**
- The paper states that more than 6000 rare diseases exist and that most still have no approved treatment or cure.
- EU orphan-drug regulation has increased approved orphan products, but approval has not eliminated access gaps.
- EU-level marketing authorisation does not guarantee equal availability across Member States because pricing, reimbursement, and launch decisions differ nationally.
- The article reports large waiting-time differences for access to the same rare-disease treatment, using the example of much shorter waits in Germany than in Poland.
- Lower-income countries are described as having longer waits and poorer access to approved orphan therapies.
- Cross-border healthcare may be crucial for rare disease patients because expertise and treatments are concentrated, but legal and administrative procedures remain complex.
- Prior authorisation and reimbursement rules can limit the practical use of cross-border care.
- The core inequality message is that formal rights and EU-level approvals can coexist with major effective-access disparities.

**Limitations**
- The article is a legal/policy argument rather than a systematic empirical study.
- It focuses on rare diseases, so its findings are not directly generalisable to population-level unmet medical examination needs.
- It does not estimate associations with GDP, unemployment, Gini, OOP share, physicians, hospital beds, or public expenditure.
- The evidence base is secondary and policy-oriented, with no causal identification strategy.
- It does not use EU-SILC, EHIS, or harmonised population survey microdata.

**Relevance for Mahdi's thesis**
- The paper is useful background for European health-system inequality: access can vary sharply across countries despite shared EU frameworks.
- It supports the thesis motivation that national context and financing/reimbursement structures matter for effective access to care.
- It is less central than EU-SILC/EHIS empirical papers because its outcome is rare-disease treatment access, not self-reported unmet need for examination.
- It can help Mahdi discuss why macro indicators and country fixed effects may capture policy fragmentation and system capacity that are not visible in individual survey variables.
- It reinforces the distinction between formal coverage or legal entitlement and actual access.

### Access to healthcare for people aged 50+ in Europe.pdf

**Citation**
Smolic, Cipin, and Medimurec (2022). Access to healthcare for people aged 50+ in Europe during the COVID-19 outbreak. European Journal of Ageing. DOI: 10.1007/s10433-021-00631-9.

**Data and setting**
- Data source: SHARE Corona Survey linked to SHARE Wave 7 and country-level COVID-19 / health-system indicators.
- Time coverage: pre-pandemic SHARE Wave 7 background information plus SHARE Corona Survey fielded in 2020 during the first COVID-19 wave.
- Countries / population: 40,919 respondents aged 50+ in 26 countries, covering 25 European countries plus Israel.
- Outcomes: three binary indicators of limited access after the COVID-19 outbreak: forgone medical treatment because of fear of infection, pre-scheduled care postponed by the provider, and requested appointment/treatment not obtained.
- Country-level covariates include COVID-19 cases and deaths per 100,000, healthcare system type, Universal Health Coverage effective coverage index, Oxford Containment and Health Index, and Old Europe / New Europe grouping.
- The authors note an important denominator limitation: respondents saying "no" may include both those with no need and those with need but no barrier, so access problems are probably underestimated.

**Main research questions**
The paper asks how access to healthcare among older Europeans was disrupted during the first COVID-19 wave and whether individual vulnerability and country-level conditions explain variation in forgone, postponed, and denied care. It separates fear-driven patient avoidance from provider-side postponement and inability to obtain appointments. For Mahdi, the paper is relevant because it combines individual access outcomes with macro/system indicators and cross-country heterogeneity.

**Methods**
- Pooled logistic regression with country controls.
- Multilevel logistic regression with individuals nested in countries and random country intercepts.
- Country-level variables are added one at a time because of high correlation among macro indicators.
- Individual controls include age, sex, education, living arrangement, rural/urban residence, job status, ability to make ends meet, pre-COVID self-rated health, change in health, major illness, prescription drug use, hospitalisation, ADL/IADL limitations, and chronic conditions.
- Null-model intraclass correlations indicate country-level clustering: 6.3% for forgone care, 15.5% for postponed care, and 7.7% for denied care.

**Key findings (for unmet need / access / inequality)**
- Overall, 12.4% reported forgone care, 27% had pre-scheduled care postponed, and 5.2% were denied requested healthcare after the outbreak.
- There was strong cross-country variation: forgone care ranged from 4.2% in Spain to 22.9% in Israel; postponed care from 1.5% in Bulgaria to 50.4% in Luxembourg; denied care from 0.7% in Bulgaria to 11.1% in Lithuania.
- Limited access was more common among women, occupationally active respondents, more educated respondents, and urban residents; the oldest age groups were less likely to report all three barriers.
- Economic difficulty mattered: great difficulty making ends meet increased odds of forgoing care and being denied care.
- Poor health was strongly associated with all three outcomes; poor self-rated health, worsened health since the outbreak, prescription drug use, and multiple chronic conditions raised the probability of reporting access problems.
- More COVID-19 cases per 100,000 were associated with postponed and denied care; more deaths per 100,000 were associated with denied care.
- Higher UHC effective coverage and stricter containment / health policies were associated with more postponed care, suggesting that systems with broad service use and strong restrictions still faced major disruption.
- New Europe countries had lower odds of forgone and postponed care than Old Europe countries; Beveridge versus Bismarck system type was not significant.

**Limitations**
- The outcomes are pandemic-specific and are not directly comparable with standard Eurostat EU-SILC unmet medical need indicators.
- Negative responses cannot separate no need from met need, producing likely downward bias in unmet-access estimates.
- The study is observational and mostly cross-sectional for the pandemic period.
- The older-adult SHARE population excludes younger adults and institutionalised populations.
- Macro variables are highly correlated, limiting joint country-level modelling.

**Relevance for Mahdi's thesis**
- The paper supports the importance of country heterogeneity and macro/system covariates when studying unmet need in Europe.
- It highlights that access barriers differ by reason: fear-driven forgone care, provider postponement, and appointment unavailability do not have identical predictors.
- Economic strain and poor health are consistent individual-level correlates that can motivate Mahdi's use of poverty, unemployment, and inequality indicators at country-year level.
- The multilevel design is a useful comparator for Mahdi's national panel and ML approach: it models individuals nested in countries rather than country-year aggregates.
- The paper is especially useful for discussing shock periods and time-aware validation, since COVID-19 disruptions may behave differently from ordinary access barriers.

### Economic crisis, austerity and unmet.pdf

**Citation**
Zavras, Zavras, Kyriopoulos, and Kyriopoulos (2016). Economic crisis, austerity and unmet healthcare needs: the case of Greece. BMC Health Services Research. DOI: 10.1186/s12913-016-1557-5.

**Data and setting**
- Data sources: Eurostat EU-SILC annual data and two Greek national health surveys conducted by the National School of Public Health.
- Time coverage: EU-SILC 2004-2011; national surveys in 2006 and 2011.
- Country / population: Greece; the national surveys included 4003 respondents in 2006 and 6569 respondents in 2011, with a final analytic sample of 3120 respondents reporting unmet needs.
- EU-SILC outcome: percentage of people who had medical needs but did not use healthcare services.
- Survey outcome: unmet healthcare needs due to financial reasons.
- Macro/time variables include median income, unemployment, and period indicators for pre-crisis years, early crisis without austerity, and crisis with austerity measures.

**Main research questions**
The paper investigates whether the Greek economic crisis and subsequent austerity measures were associated with increased unmet healthcare needs. It also asks which socioeconomic and insurance characteristics predict non-utilisation of healthcare due to financial reasons. For Mahdi, the paper is a direct crisis-period example linking EU-SILC unmet need, unemployment, income, and financial barriers.

**Methods**
- Time-series ordinary least squares models using EU-SILC annual data.
- Augmented Dickey-Fuller tests, cointegration/residual stationarity checks, AIC/BIC model comparison, and residual diagnostics.
- Multivariate logistic regression using pooled 2006 and 2011 national survey data.
- Individual covariates include year, sex, age, health status, chronic disease, education, income, employment, insurance status, and prefecture.
- Model diagnostics include link test, ROC/AUC, and Hosmer-Lemeshow goodness-of-fit.

**Key findings (for unmet need / access / inequality)**
- The austerity period 2010-2011 was associated with a statistically significant increase in EU-SILC unmet healthcare need compared with 2004-2007; the early crisis period 2008-2009 was not statistically significant.
- In the national surveys, the odds of non-utilisation due to financial reasons were 44% higher in 2011 than in 2006.
- Income was a strong predictor: lower-income groups had much higher odds of financial unmet need than higher-income groups.
- Lower education increased the odds of unmet need due to financial reasons.
- Unemployment increased the odds of financial non-utilisation compared with employment.
- Insurance coverage was protective; public insurance and private insurance both lowered the odds of financial unmet need relative to being uninsured.
- Sex, age, self-rated health, chronic disease, urbanity, and prefecture were not significant in the authors' financial-barrier model.
- The authors emphasise income, unemployment, and insurance as the key economic channels through which austerity translated into access barriers.

**Limitations**
- The EU-SILC time series is short, which limits robustness of the OLS results.
- The analysis does not cover the later and deeper 2012-2015 phase of the Greek recession.
- The authors note that panel data would be preferable but were unavailable.
- Self-reported unmet need combines access constraints, preferences, expectations, and reporting behaviour.
- The design is associational and cannot fully identify causal effects of austerity.

**Relevance for Mahdi's thesis**
- This is a highly relevant EU-SILC source for motivating unemployment, income, poverty, and insurance / social-protection covariates.
- It supports including period shocks or time effects in a European panel because crisis and austerity years can shift unmet need sharply.
- The single-country design contrasts with Mahdi's cross-country panel and ML models, giving Mahdi a gap to fill with broader European prediction.
- The paper reinforces the importance of financial reasons for unmet need, especially during macroeconomic stress.
- It is a useful cautionary citation on limited causal interpretation when using aggregate time-series or repeated cross-sectional survey data.

### Economic vulnerability and unmet healthcare needs.pdf

**Citation**
Arnault, Jusot, and Renaud (2022). Economic vulnerability and unmet healthcare needs among the population aged 50+ years during the COVID-19 pandemic in Europe. European Journal of Ageing. DOI: 10.1007/s10433-021-00645-3.

**Data and setting**
- Data source: SHARE Wave 8 linked to the SHARE Corona Survey.
- Time coverage: Wave 8 interviews from October 2019 to March 2020 and SHARE Corona Survey in June-July 2020.
- Countries / population: 31,819 adults aged 50+ in private households across 26 European countries.
- Outcomes: forgone healthcare due to fear of COVID-19, planned care postponed by provider, and inability to obtain a medical appointment or treatment.
- Key exposure: pre-pandemic economic vulnerability, defined by some or great difficulty making ends meet.
- Additional covariates include age, sex, partnership, country, baseline health, chronic conditions, obesity, previous GP/specialist/dental use, education, and income quartile.

**Main research questions**
The paper asks whether economically vulnerable older adults faced greater unmet healthcare needs during the first COVID-19 wave in Europe. It also examines whether vulnerability effects differ by type of unmet need, country, and baseline health status. For Mahdi, this is a strong example of inequality-oriented modelling of access barriers with cross-country heterogeneity.

**Methods**
- Separate probit models for each unmet-need outcome.
- Sequential adjustment: demographic/country controls, then baseline health needs and utilisation, then education and income quartile.
- Results are presented as average marginal effects.
- Country-specific models explore heterogeneity in the association between economic vulnerability and unmet need.
- Interaction models examine whether economic vulnerability has larger effects among respondents in poor baseline health.
- Country-specific survey weights are used to preserve representativeness by age, sex, and region.

**Key findings (for unmet need / access / inequality)**
- Descriptive prevalence was high: approximately 25% reported postponed planned care, 12% forgone care due to fear, and 5% inability to obtain an appointment.
- Economically vulnerable respondents made up 36% of the sample and had lower education, lower income, worse health, more GP use, and less dental use.
- In the fully adjusted model, economic vulnerability increased the risk of forgoing care due to fear by about 1.5 percentage points and inability to obtain an appointment by about 0.7 percentage points.
- Economic vulnerability was not significantly associated with postponed planned care in the overall model.
- Poor health and prior healthcare utilisation were strong predictors of all three access-disruption outcomes.
- Vulnerability effects differed substantially by country; positive effects appeared in some countries and negative or null effects in others.
- Among respondents in poor baseline health, economic vulnerability had larger effects on postponed care, forgoing care, and inability to obtain care, showing cumulative medical and economic vulnerability.
- International differences did not map neatly onto pre-pandemic rankings of social inequality, suggesting that pandemic policy and health-system response mattered.

**Limitations**
- SHARE Corona questions were new and pandemic-specific, so interpretation may differ across respondents and countries.
- The study focuses on older adults in private households and does not cover the full adult population.
- The pandemic survey may contain selection or participation bias.
- Baseline health is measured through available SHARE health items and may not capture all relevant clinical need.
- The analysis is observational and does not identify causal effects of economic vulnerability.

**Relevance for Mahdi's thesis**
- The paper supports including poverty, financial strain, income-distribution, and unemployment-type indicators in models of unmet need.
- It shows that access barriers are reason-specific and may respond differently to economic vulnerability.
- Country heterogeneity and interaction with poor health motivate flexible modelling, including regularised regression and tree-based methods that can capture nonlinearities.
- The study complements Mahdi's aggregate Eurostat panel by showing individual-level mechanisms behind country-level inequality signals.
- It is useful for the thesis discussion of COVID-era observations as structurally different from normal-period access dynamics.

### Effects of the financial crisis and Troika austerity measures.pdf

**Citation**
Legido-Quigley et al. (2016). Effects of the financial crisis and Troika austerity measures on health and health care access in Portugal. Health Policy. DOI: 10.1016/j.healthpol.2016.04.009.

**Data and setting**
- Data sources: EU-SILC microdata, OECD and Eurostat indicators, Portuguese Ministry of Health sources, official statistics, grey literature, and supporting qualitative / quantitative studies.
- Main quantitative comparison: EU-SILC 2010 and 2012, around the introduction of Troika adjustment and austerity measures.
- Country / population: Portugal, respondents aged 16-80 in the EU-SILC analysis.
- Outcome: perceived unmet medical need over the previous 12 months, with supplementary reasons.
- Reasons include financial barriers, waiting times, inability to take time off work or family responsibilities, distance/transport, and waiting to see whether the problem resolved.
- Policy context includes co-payment increases, exemption procedures, reduced public funding share, and increased private/OOP financing.

**Main research questions**
The paper assesses how the Portuguese financial crisis and Troika austerity measures affected health and healthcare access. It focuses on whether unmet medical need increased after austerity and whether different labour-market groups were affected differently. For Mahdi, it provides a clear EU-SILC example connecting austerity, OOP exposure, public financing, and access inequality.

**Methods**
- Weighted logistic regression using EU-SILC data for 2010 and 2012.
- The key exposure is crisis/austerity timing, comparing 2012 with 2010.
- Models are stratified by economic status: employed, unemployed, retired, and other inactive.
- Adjusted covariates include age, sex, marital status, and education.
- The regression evidence is combined with narrative synthesis of expenditure, utilisation, policy reforms, and health-system workforce evidence.

**Key findings (for unmet need / access / inequality)**
- Odds of reporting unmet medical need more than doubled in 2012 compared with 2010.
- The proportional increase was largest among employed respondents, followed by unemployed, retired, and other inactive groups.
- Financial barriers increased substantially after austerity.
- Waiting-time barriers also increased, showing that access problems were not only affordability-related.
- Inability to take time off work or family responsibilities became more common as a reason for unmet need.
- A very large increase was reported for delaying care while waiting for the problem to resolve, although the authors warn that reason-specific counts are small.
- Public health funding share fell while private expenditure increased; OOP payments represented a large share of private health spending.
- Co-payment increases and bureaucratic exemption barriers likely affected vulnerable and disadvantaged groups despite formal protections.

**Limitations**
- The unmet-need measure is self-reported and may reflect reporting behaviour as well as realised access barriers.
- EU-SILC does not quantify how many times respondents experienced unmet need.
- Reason-specific results are based on smaller counts and should be interpreted cautiously.
- The article combines regression with grey literature because peer-reviewed evidence on Portugal during the period was still limited.
- The design is before/after and associational, not a strict causal evaluation of Troika measures.

**Relevance for Mahdi's thesis**
- This is directly relevant because it uses EU-SILC unmet medical need and focuses on a European austerity setting.
- It motivates inclusion of OOP share, public expenditure, income/employment conditions, and policy-period controls in macro-level models.
- It shows why financial and waiting-time reasons should be interpreted separately when possible.
- The Portugal case provides substantive context for Southern European country-year patterns in Mahdi's Eurostat panel.
- It also supports Mahdi's predictive / associational framing because strong policy timing associations remain difficult to interpret causally.

### Investigating unmet need for healthcare.pdf

**Citation**
Moran, Suhrcke, Ruiz-Castell, Barre, and Huiart (2021). Investigating unmet need for healthcare using the European Health Interview Survey: a cross-sectional survey study of Luxembourg. BMJ Open. DOI: 10.1136/bmjopen-2021-048860.

**Data and setting**
- Data source: European Health Interview Survey wave 2 for Luxembourg.
- Time coverage: February-December 2014.
- Country / population: Luxembourg residents aged 15+ in private households and registered with the national health insurance fund; final validated EHIS sample of 4004.
- EHIS differs from EU-SILC because it does not ask one global binary unmet-need question; it asks barrier-specific questions.
- Outcomes among respondents reporting need: unmet need due to waiting time, distance/transport, inability to afford medical care, inability to afford dental care, inability to afford prescribed medicines, and inability to afford mental healthcare.
- Respondents reporting no need for the relevant service are coded missing for that outcome.

**Main research questions**
The paper estimates the prevalence and determinants of several types of unmet healthcare need in Luxembourg, a high-income country with broad coverage and high public health spending. It asks whether barriers remain despite favourable health-system resources and which socioeconomic and health-status groups are most affected. For Mahdi, it is useful for interpreting Eurostat indicators by reason and for showing that low national average unmet need can hide service-specific inequality.

**Methods**
- Cross-sectional survey analysis using multivariate logistic regression for each unmet-need outcome.
- Sample weights are used to represent the Luxembourg population by age, sex, and district.
- Robust standard errors are reported.
- Covariates include sex, age, marital status, immigrant status, education, job status, household income quintile, social support, informal caring, BMI, smoking, alcohol use, self-assessed health, chronic disease, activity limitations, and canton fixed effects.
- Missing covariates are excluded in the main models; a sensitivity analysis adds a missing-income indicator.

**Key findings (for unmet need / access / inequality)**
- Waiting time was the most common barrier, affecting about 32% of those with need.
- Distance/transport was least common, around 4%.
- Affordability barriers were meaningful even in Luxembourg: around 15% reported at least one affordability problem, with dental care most common, followed by prescribed medicines, medical care, and mental healthcare.
- Bad or very bad self-assessed health was strongly associated with every unmet-need component, including waiting, distance, medical affordability, dental affordability, medicines, and mental healthcare.
- Higher income was protective, especially for dental care, prescribed medicines, and mental healthcare.
- Moderate or high social support was protective for dental, medicines, and mental healthcare affordability barriers.
- Women, respondents with chronic conditions, and respondents with activity limitations were more likely to report waiting-time unmet need; older respondents were less likely than young adults to report waiting-time barriers.
- The study shows that financial access problems can persist even where public expenditure is high, OOP share is low, and formal benefits are broad.

**Limitations**
- The study is cross-sectional and cannot support causal interpretation.
- All unmet-need measures are self-reported and subject to recall, expectation, and response bias.
- EHIS does not provide detailed information on the type of service involved in waiting-time barriers.
- The sampling frame excludes homeless people, undocumented migrants, people outside formal coverage, institutionalised populations, and others likely to face severe access barriers.
- Response rate was low and income missingness was high, which may affect estimates.

**Relevance for Mahdi's thesis**
- The paper is highly useful for measurement discussion because EHIS separates waiting, distance, and affordability barriers more explicitly than a single global unmet-need indicator.
- It supports using poverty and inequality covariates because income gradients remain visible even in a high-resource health system.
- It shows that health status and morbidity are important demand-side factors that may confound or mediate observed macro associations.
- The Luxembourg case cautions against interpreting high GDP or public spending as sufficient for low unmet need across all services.
- It complements Mahdi's country-year Eurostat analysis by providing service-specific micro evidence that aggregate hlth_silc_08/08b cannot fully reveal.

### Karanikolos-2016-Access-to-care-in-the-baltic-states.pdf

**Citation**
Karanikolos, Gordeev, Mackenbach, and McKee (2016). Access to care in the Baltic States: did crisis have an impact? European Journal of Public Health. DOI: 10.1093/eurpub/ckv205.

**Data and setting**
- Data source: Eurostat EU-SILC cross-sectional microdata.
- Time coverage: 2005-2012, with 2009 used as the baseline because the EU-SILC unmet-need question refers to the previous 12 months and 2009 predates the main crisis-policy effects.
- Countries / population: Estonia, Latvia, and Lithuania; representative population survey respondents.
- Outcome: self-reported unmet need for medical examination or treatment during the last 12 months.
- Reasons analysed: could not afford care, waiting list, could not take time because of work/family responsibilities, too far to travel, wanted to wait and see if the problem resolved, and other reasons.
- Policy setting: deep 2009 GDP contractions and severe but different austerity responses across the three Baltic health systems.

**Main research questions**
The paper asks whether the economic crisis and post-crisis austerity measures worsened access to medical care in Estonia, Latvia, and Lithuania. It also asks whether different health-system financing and policy responses produced different unmet-need patterns. For Mahdi, it is a direct EU-SILC crisis-period paper showing that country-specific system responses can change both the level and reason composition of unmet need.

**Methods**
- Age-adjusted prevalence trends using the 2013 European Standard Population.
- Log-binomial regressions estimating the risk of unmet medical need in 2010-2012 relative to 2009.
- Separate regressions by reason for unmet need.
- Models adjust for age, sex, marital status, and education.
- EU-SILC standard population weights are used to account for survey design.
- The analysis is repeated separately for each Baltic country rather than pooled as a panel model.

**Key findings (for unmet need / access / inequality)**
- Latvia had the highest unmet need throughout 2005-2012; it fell from 29.6% in 2005 to 15.4% in 2009, then rose above 21% in 2010-2011 and remained 18.6% in 2012.
- Estonia fell to 5.0% unmet need in 2009, then increased steadily to 8.6% by 2012.
- Lithuania fell to 3.3% in 2009 and remained broadly stable after the crisis, at 3.5% in 2012.
- Compared with 2009, unmet need increased significantly in Latvia in 2010, 2011, and 2012, and in Estonia especially by 2011-2012; Lithuania showed no significant deterioration.
- Latvia's increase was mainly driven by inability to afford care; this matches Latvia's increased co-payments, higher caps on user charges, and reduced exemption thresholds.
- Estonia's increase was mainly driven by waiting lists, consistent with implicit rationing through longer official waiting times and provider payment reductions rather than higher user charges.
- Lithuania's stable unmet need is interpreted as evidence that deterioration was not inevitable when policy protected service availability or when efficiency gains could absorb provider-payment cuts.
- Better financial preparedness in Estonia and Lithuania helped prevent a rise in cost-related unmet need, although Estonia still experienced waiting-time barriers.

**Limitations**
- EU-SILC unmet need is self-reported and perceptions may differ within and between countries over time.
- The number of respondents reporting unmet need is relatively small, reducing power for reason-specific estimates.
- The paper lacks comparable service-utilisation data to validate whether self-reported unmet need corresponds to actual changes in care use.
- The design cannot establish a direct causal relationship between crisis/austerity and unmet need.
- The study covers only three countries and a short post-crisis window.

**Relevance for Mahdi's thesis**
- This is highly relevant because it uses the same EU-SILC unmet medical examination/treatment family of indicators.
- It motivates including macroeconomic crisis years, unemployment/GDP context, OOP/payment variables, and health-system capacity measures.
- It shows that reason-specific unmet need matters: the same macro shock can appear as affordability barriers in one country and waiting-time barriers in another.
- It supports Mahdi's use of country effects or flexible ML models because baseline barriers and system responses differ sharply by country.
- It is a useful non-causal precedent: the paper interprets crisis-policy associations without claiming strict causal identification.

### maslyankov-2024-unmet-healthcare-needs-in-southeastern-europe-a-systematic-review.pdf

**Citation**
Maslyankov (2024). Unmet healthcare needs in Southeastern Europe: a systematic review. The Journal of Medicine Access. DOI: 10.1177/27550834241255838.

**Data and setting**
- Data source: systematic review of quantitative evidence identified through Medline, Embase, EconLit, Google searches, Bulgarian-language searches, and reference checking.
- Search date: July 2023.
- Eligible publication period: after 2003.
- Countries / population: Albania, Bosnia and Herzegovina, Bulgaria, Greece, Kosovo, Montenegro, Serbia, North Macedonia, and Romania.
- Included evidence: 23 quantitative publications using self-reported unmet healthcare needs as an access indicator.
- Common survey sources include EU-SILC, EHIS, SHARE, WHO financial protection reports, and national surveys.
- Outcomes vary by study but generally cover self-reported unmet medical, dental, primary-care, inpatient, or general healthcare needs and reasons such as cost, waiting time, distance, and other barriers.

**Main research questions**
The review asks what quantitative evidence exists on self-reported unmet healthcare needs in Southeastern Europe and what patterns emerge across countries and population groups. It focuses on prevalence, determinants, barriers, and evidence quality. For Mahdi, it provides a regional synthesis for Balkan/Southeastern European contexts where access barriers are often financial and evidence quality is uneven.

**Methods**
- Systematic literature review following PRISMA reporting principles.
- Inclusion criteria required quantitative studies or reports using self-reported unmet healthcare need as an access measure.
- Quality appraisal used the AXIS tool for cross-sectional studies.
- Data extraction captured country, population, data source, survey year, sampling strategy, sample size, unadjusted prevalence, adjustment methods, significant predictors, and contextual events.
- No meta-analysis or pooled quantitative synthesis was performed because study designs, outcomes, and surveys were too heterogeneous.
- Evidence was narratively synthesised by country and by recurring themes.

**Key findings (for unmet need / access / inequality)**
- Evidence is uneven: Greece has the most studies, followed by Bulgaria and Romania; Western Balkan countries have much thinner evidence, and no Kosovo study was identified.
- Pan-European surveys are common; EU-SILC appears in 10 included studies, EHIS in 4, and SHARE in 1.
- Almost half of the included studies are descriptive only; among analytical studies, most use logit/probit regression but covariate sets differ substantially.
- In Bulgaria, unmet medical and dental needs decreased markedly over time, from high levels in the late 2000s to below the EU average in more recent years, but socioeconomic and rural/urban inequalities persisted.
- In Greece, evidence consistently links unmet need to the economic crisis/austerity context, with cost as the dominant barrier and higher burden among migrants, disabled people, lower-education groups, low-income groups, and unemployed people.
- In Romania, unmet medical and dental needs declined between 2011 and 2017 and then stabilised, with high costs, especially medicines, as the main barrier.
- In Serbia, studies report high prevalence and identify financial resources, education, rural residence, income, and health status as important predictors, although one study found unemployment associated with lower reported need after adjustment.
- Across the region, high cost is the most consistent barrier; waiting time is less dominant than in many Western European systems.

**Limitations**
- The review excludes literature in languages other than English and Bulgarian, which may omit relevant country-specific studies.
- Included studies are heterogeneous and often low quality, limiting cross-country comparability.
- The evidence base is skewed toward Greece, Bulgaria, and Romania, leaving major gaps for parts of the Western Balkans.
- No quantitative pooling was possible because survey questions, populations, and analytic designs differ.
- The review is dependent on published and indexed evidence, so publication and language bias are plausible.

**Relevance for Mahdi's thesis**
- This is a useful regional background citation for Southeastern Europe and the Balkans, where Mahdi may observe high or volatile unmet need.
- It supports prioritising cost/OOP, poverty, income, education, rurality, and migrant/minority vulnerability as access-inequality mechanisms.
- It shows that EU-SILC is widely used but not always analysed with comparable covariates or methods, leaving space for Mahdi's harmonised panel/ML approach.
- The review's evidence-quality concerns help justify a careful, transparent modelling workflow and cautious interpretation.
- It can support the thesis argument that national averages should be read alongside structural inequalities and regional evidence gaps.

### Older_Europeans_experience_of_unmet_health_care_d.pdf

**Citation**
Tavares (2022). Older Europeans' experience of unmet health care during the COVID-19 pandemic (first wave). BMC Health Services Research. DOI: 10.1186/s12913-022-07563-9.

**Data and setting**
- Data source: SHARE COVID-19 Survey, with selected variables from SHARE Wave 7 and macro indicators from Eurostat and Oxford COVID-19 Government Response Tracker.
- Time coverage: SHARE COVID-19 data collected by CATI in June-July 2020; macro/system variables generally from 2018-2019 or first-wave policy response.
- Countries / population: 23,288 non-institutionalised people aged 50+ in 25 EU countries covered by SHARE.
- Outcomes: forgoing medical treatment due to fear of infection, provider-postponed medical appointment, failure to obtain requested appointment/treatment, and an overall unmet-care indicator.
- Individual covariates include sex, age, education, household income, difficulty making ends meet, pandemic unemployment, self-assessed health, worsened health, and chronic diseases.
- Macro/system covariates include Beveridge system type, high OOP share, pre-pandemic high unmet need among older people, doctors, nurses, hospital beds per 100,000, and no-lockdown indicator.

**Main research questions**
The paper asks how unmet health care among older Europeans varied across countries during the first COVID-19 wave and which individual and health-system factors were associated with forgoing, postponement, or denial of care. It explicitly tests whether system characteristics and government lockdown decisions relate to unmet care. For Mahdi, it is highly relevant because it connects individual access outcomes to OOP, doctors, nurses, beds, system type, and pre-pandemic unmet-need levels.

**Methods**
- Six logistic regressions: three with country controls to study individual factors and three with macro/system controls to study health-system factors.
- Outcomes are modelled separately for forgone care, postponed care, and denied care.
- Results are reported as odds ratios and average marginal effects.
- Standard errors use country-clustered sandwich estimators.
- Diagnostic checks include VIF for multicollinearity, link tests, pseudo-R2, Wald tests, Pearson goodness-of-fit, and Hosmer-Lemeshow tests.
- Analysis conducted in Stata 15.

**Key findings (for unmet need / access / inequality)**
- Country variation was large: Luxembourg had just over 35% reporting some unmet care, while Romania was around 7%.
- The reason composition differed by country: Luxembourg had the highest postponement, Lithuania the highest denial, Spain the lowest forgoing, and Germany the highest forgoing.
- Women, younger older adults, more educated respondents, higher-income respondents, those with difficulty making ends meet, and people with worse health were more likely to report unmet care in at least some models.
- Difficulty making ends meet increased the odds of forgoing care by about 33%, but it was not significant for postponement or denial.
- Worsened health during the pandemic increased odds of all three outcomes: about 55% higher for forgone care, 18.5% higher for postponed care, and roughly twice as high for denied care.
- Poorer self-assessed health and more chronic diseases also increased unmet-care reporting.
- High-OOP countries had higher odds of forgoing care, consistent with financial pressure and household budget constraints.
- Beveridge systems were associated with lower odds of postponed care; hospital beds mattered only weakly for postponement, and no single health-system characteristic explained all unmet care forms.

**Limitations**
- SHARE COVID questions are pandemic-specific and had not been previously validated.
- Outcomes do not identify service type, intensity, frequency, private insurance status, or whether the reported demand was clinically necessary need.
- SHARE excludes institutionalised people and focuses on adults aged 50+, so results do not generalise to all adults.
- Survey bias, including selection, attrition, and reporting bias, may affect estimates.
- The analysis cannot include all relevant health-system factors, such as equipment, information systems, organisation, and provider-level adaptations.

**Relevance for Mahdi's thesis**
- The paper directly supports Mahdi's inclusion of OOP share, doctors, nurses, hospital beds, and system-level variables in access models.
- It shows that macro indicators can matter differently by unmet-need reason, which is important when comparing hlth_silc_08 and 08b reason categories.
- The health-status results remind Mahdi that country-year models without individual need controls capture both access barriers and underlying population health composition.
- The finding that no single health-system characteristic explains all unmet care supports using multiple model families and cautious interpretation.
- It is useful for discussing pandemic years as special observations that may need time-aware validation or sensitivity analysis.

### Predictors of unmet health care needs in.pdf

**Citation**
Popovic, Terzic-Supic, Simic, and Mladenovic (2017). Predictors of unmet health care needs in Serbia; Analysis based on EU-SILC data. PLOS ONE. DOI: 10.1371/journal.pone.0187866.

**Data and setting**
- Data source: Survey on Income and Living Conditions (SILC) in the Republic of Serbia, collected by the Statistical Office of Serbia using EU-SILC methodology.
- Time coverage: 2014.
- Country / population: Serbia excluding Kosovo and Metohija; 20,069 people in sampled households, with 16,219 respondents aged 16+ answering health questions; response rate 80.8%.
- Outcome: self-perceived unmet healthcare need based on whether the respondent should have visited a doctor in the past 12 months but did not.
- Reasons include too expensive, waiting list, too far to travel, could not take time because of work/care, fear of doctor/hospital/testing/treatment, wanted to wait and see, did not know a good doctor/specialist, and other reasons.
- Reasons are grouped into availability, accessibility, acceptability, and health-system responsibility categories.

**Main research questions**
The paper estimates the prevalence of unmet healthcare needs in Serbia and identifies demographic, socioeconomic, regional, and health-status predictors. It also decomposes reasons into system-responsibility barriers and respondent-preference/acceptability barriers. For Mahdi, it is useful because it is EU-SILC-based, focused on a Southeastern European country, and separates financial, waiting, distance, and personal-reason mechanisms.

**Methods**
- Cross-sectional secondary analysis of SILC 2014.
- Andersen's Behavioral Model of Health Services Use structures predictors as predisposing, enabling, and need factors.
- Pearson chi-square tests compare respondents with met and unmet needs.
- VIF checks assess multicollinearity.
- Nine multivariate logistic regression models are estimated.
- Main models predict overall unmet need, availability barriers, accessibility barriers, acceptability barriers, and health-system responsibility; additional models predict unmet need by Serbian region.
- Odds ratios and 95% confidence intervals are reported.

**Key findings (for unmet need / access / inequality)**
- 14.9% of Serbian respondents aged 16+ reported unmet healthcare needs, higher than the EU-SILC average cited by the authors for 28 European countries.
- Health-system-responsibility reasons accounted for 58.2% of unmet need, while acceptability/personal circumstances accounted for 41.7%.
- The most common reason was cost/too expensive (36.6%), followed by wanting to wait and see if the problem got better (18.3%), waiting lists (17.7%), lack of time due to work/care (16.1%), fear (5.7%), distance (3.9%), and not knowing a good doctor/specialist (1.6%).
- In the overall model, very bad self-perceived health strongly increased unmet need (OR 6.37), and poor/fair/bad health categories also had large associations.
- Higher income strongly reduced unmet need; the richest quintile had much lower odds than the poorest quintile (OR 0.46 overall, and 0.09 for accessibility barriers).
- Higher education reduced overall unmet need and accessibility/responsibility barriers, although it did not reduce availability barriers.
- Divorced/widowed respondents had higher odds of overall unmet need and health-system-responsibility barriers.
- Region mattered: Sumadija and Western Serbia had higher odds of overall unmet need, accessibility barriers, acceptability barriers, and system-responsibility barriers than Belgrade.

**Limitations**
- The study is cross-sectional and cannot identify causal effects.
- Unmet need and health status are self-reported and influenced by expectations, social context, and reporting behaviour.
- The sample excludes people living in health and social-care institutions, who may have more severe health conditions.
- Some findings, such as lower adjusted odds among unemployed/inactive people, may reflect work-time constraints, formal insurance issues, or reporting patterns rather than lower true need.
- Serbia-specific regional and institutional context limits direct generalisation to the EU panel.

**Relevance for Mahdi's thesis**
- This is a directly relevant EU-SILC-family paper for a Southeastern European setting.
- It supports poverty/income, regional context, health status, and education as major predictors of unmet need.
- The reason grouping is useful for Mahdi's interpretation of Eurostat 08b categories: affordability, waiting, distance, and personal preference capture different mechanisms.
- The paper shows why macro-level models may need to treat regional/country fixed effects as proxies for local service organisation and geography.
- It provides a useful comparator for Mahdi's national-level panel: micro-level logistic models identify individual mechanisms that aggregate Eurostat variables only approximate.

### Predictors of Unmet Healthcare Needs during Economic and.pdf

**Citation**
Pierrakos, Goula, and Latsou (2023). Predictors of Unmet Healthcare Needs during Economic and Health Crisis in Greece. International Journal of Environmental Research and Public Health. DOI: 10.3390/ijerph20196840.

**Data and setting**
- Data source: Eurostat database, including EU-SILC unmet-need indicators and Eurostat demographic, socioeconomic, health, GDP, labour-market, and health-expenditure indicators.
- Time coverage: mainly 2008-2022, with some indicators available from shorter periods such as 2011-2022, 2012-2021, or 2013-2022.
- Country / population: Greece, with comparisons to EU27 and breakdowns by region, income quintile, and occupational status.
- Main outcome: self-reported unmet need for medical care due to too expensive, too far to travel, or waiting list, using Eurostat indicator TESPM110 / EU-SILC family indicators.
- Additional outcomes/descriptive indicators include unmet dental care, regional unmet medical need, income-quintile unmet need, and employed/unemployed unmet need.
- Predictors include public and private health expenditure, self-perceived health, long-standing limitations, GDP per capita, employment rate, and unemployment rate.

**Main research questions**
The paper asks how unmet medical needs evolved in Greece through the financial crisis and COVID-19 health crisis, and which Eurostat indicators are associated with unmet need. It focuses on income, occupational status, region, health status, functional limitation, and public/private health spending. For Mahdi, it is relevant because it uses Eurostat time-series indicators close to his national panel design, though for one country only.

**Methods**
- Descriptive analysis comparing Greece with EU27 by year, dental need, region, income quintile, and occupational status.
- Pearson correlation analysis between unmet medical need and candidate indicators.
- Eight simple linear regression models, each with unmet medical need as the dependent variable and one predictor entered separately.
- Statistical significance threshold p <= 0.05.
- Analysis conducted in SPSS 25.
- The design is ecological/time-series and does not use multivariable panel modelling.

**Key findings (for unmet need / access / inequality)**
- Greece's unmet medical need was similar to EU27 around 2010 but diverged sharply during the economic crisis; Greece reached roughly triple the EU27 level during the crisis period.
- Greek unmet needs declined gradually after 2017 but remained high relative to EU27, and increased again around the pandemic period.
- Dental unmet need was especially high in Greece, reaching 14.9% in 2014 and 12.1% in 2022, far above EU27 levels; the paper attributes this largely to financial barriers and limited public dental coverage.
- Regional inequality is substantial: Eastern Macedonia and Thrace had around 10% unmet medical need in 2020, with high levels also in the Northern Aegean, Northern Greece, and Central Macedonia.
- Income gradients are large: in 2022, about 27% of people in the first and second Greek income quintiles reported unmet medical needs compared with 6.5% in the EU27; the highest quintile was around 1%.
- Unemployed people had much higher unmet need than employed people in Greece, approximately 12.5% versus 5%, compared with 4.6% and 1.7% in the EU27.
- Unmet medical need correlated positively with bad/very bad self-perceived health, long-standing limitations, and unemployment.
- It correlated negatively with private and public health expenditure, very good/good health, real GDP per capita, and employment rate.

**Limitations**
- The analysis is based on self-reported unmet need, health status, and activity limitation, so subjective reporting and cultural response differences matter.
- EU-SILC excludes institutionalised populations, which can understate poor health but may also overstate unmet need if excluded institutionalised people receive continuous care.
- The regression models are simple bivariate time-series models and do not adjust simultaneously for correlated macro indicators.
- The paper explicitly notes endogeneity between health status and unmet need; contemporaneous associations cannot establish direction of causality.
- Greece-only evidence is highly relevant substantively but not sufficient for European cross-country inference.

**Relevance for Mahdi's thesis**
- This paper is closely aligned with Mahdi's Eurostat-based design and provides Greek time-series context for crisis and pandemic years.
- It supports including unemployment, GDP per capita, public expenditure, private/OOP expenditure, and health-status proxies where available.
- The strong income-gradient and regional findings support the thesis motivation that national averages can mask inequality.
- Methodologically, the paper highlights a gap: Mahdi can improve on bivariate correlations by using multivariable panel models, regularisation, and time-aware validation.
- It reinforces Mahdi's non-causal framing because macro indicators, health status, and unmet need are jointly determined.

### Unmet Health Care Needs of the Older Population in European.pdf

**Citation**
Kocot (2023). Unmet Health Care Needs of the Older Population in European Countries Based on Indicators Available in the Eurostat Database. Healthcare. DOI: 10.3390/healthcare11192692.

**Data and setting**
- Data source: Eurostat database, using the European Health Interview Survey (EHIS) unmet-healthcare-need indicator.
- Time coverage: 2019, selected as the last pre-COVID year available for this EHIS-based analysis.
- Countries / population: 26 EU countries plus Iceland and Norway; individuals in private households, with comparisons across ages 15-64, 65+, 65-74, and 75+.
- Outcome: share of people with healthcare needs in the previous 12 months whose needs were not met.
- Reasons: financial reasons, distance/transportation, and waiting lists.
- Stratifiers and potential determinants: income quintile, education, urbanization group, and activity limitation level.
- The paper explicitly compares EHIS and EU-SILC indicators and chooses EHIS because it is denominator-based on people reporting healthcare needs, while EU-SILC values are calculated for the whole population and can be very small after rounding.

**Main research questions**
The paper asks whether older Europeans differ from younger adults in the prevalence, reasons, and correlates of unmet healthcare need. It also asks whether older adults should be treated as one homogeneous group or split into ages 65-74 and 75+. For Mahdi, the study is useful because it uses Eurostat data and clarifies how age structure and reason-specific indicators can change the interpretation of national access inequalities.

**Methods**
- Cross-sectional descriptive and comparative analysis of public Eurostat aggregate data.
- Main age-group comparisons: 15-64 versus 65+, and 65-74 versus 75+.
- The author calculates reason shares among those reporting unmet need and ranges across income, education, urbanization, and activity limitation categories.
- Statistical testing includes one-way ANOVA, t-tests, Mann-Whitney U tests, Shapiro-Wilk normality tests, and Levene variance tests.
- Analyses were conducted in IBM SPSS Statistics 28.
- No individual-level regression, panel model, or causal design is used.

**Key findings (for unmet need / access / inequality)**
- The level of EHIS-based unmet need varies widely across countries and age groups; examples for total population include high values in Portugal, Luxembourg, Estonia, Latvia, Finland, Croatia, and Denmark.
- In more than half of countries, unmet need was higher among ages 15-64 than among 65+, but Poland, Croatia, and Romania had much higher unmet need among older adults.
- Within the older population, most countries had modest differences between ages 65-74 and 75+, but some country-specific gaps were meaningful.
- Waiting lists were a major reason in almost every country and age group; in most countries more than half of people with unmet need reported waiting-time problems.
- Financial reasons were reported significantly more often among ages 15-64 than among ages 65+; the mean reason share was 58.9% for ages 15-64 versus 49.3% for ages 65+.
- Distance/transportation was significantly more important for older adults than younger adults, and especially for ages 75+ compared with 65-74.
- Lower income was generally associated with higher unmet need; income-group differences were statistically significant for ages 15-64, 65+, and 65-74, but not for 75+.
- Activity limitation showed the strongest gradient: severe limitation was associated with at least twice the mean unmet-need level of no limitation in every age group, with statistically significant differences throughout.

**Limitations**
- The analysis uses aggregate Eurostat data, so it cannot model individual-level mechanisms or interactions directly.
- It is cross-sectional for 2019 and cannot assess trends or causal effects.
- Health-system financing, organisation, service capacity, and age-specific policy rules are not included as explanatory variables.
- The 65+ group is split only into 65-74 and 75+; the oldest-old group, such as 85+, cannot be isolated.
- EHIS-based unmet need is self-reported and may be affected by expectations, health literacy, response bias, and country reporting differences.

**Relevance for Mahdi's thesis**
- The paper is useful for Mahdi's measurement discussion because it explains differences between EHIS and EU-SILC unmet-need indicators.
- It supports treating reasons for unmet need separately: waiting lists, financial barriers, and distance/transport behave differently by age.
- It highlights that country-level models may be sensitive to demographic composition and age-specific access patterns.
- Activity limitation and income gradients reinforce the importance of need and socioeconomic inequality variables in unmet-need analysis.
- It provides a clear example of how Eurostat aggregate data can support policy-relevant comparisons while remaining descriptive and non-causal.

### Unmet healthcare needs among older Europeans trends,.pdf

**Citation**
Chantzaras and Yfantopoulos (2025). Unmet healthcare needs among older Europeans: trends, determinants, and the role of public health expenditure. Journal of Public Health. DOI: 10.1007/s10389-025-02543-9.

**Data and setting**
- Data source: Survey of Health, Ageing and Retirement in Europe (SHARE) panel microdata, linked to Eurostat public health expenditure.
- Time coverage: descriptive comparison between SHARE wave 1 in 2004 and wave 8 in 2019/2020; econometric analysis uses wave 8.
- Countries / population: 42,780 respondents aged 50+ across 26 European countries in the final wave-8 modelling sample; Israel excluded.
- Outcomes: overall unmet healthcare need and unmet need for general practitioner services, specialist physician services, medicines, dental services, and home care.
- Unmet need is defined as healthcare need not met due to cost or lack of availability.
- Key macro predictor: natural log of public health expenditure in euros PPS per inhabitant from Eurostat.
- Controls: age, sex, marital status, education, equivalized household income, employment, urban residence, supplementary health insurance, self-reported health, and limitations in usual activities.

**Main research questions**
The paper investigates whether higher public healthcare expenditure reduces unmet healthcare needs among older Europeans. It also documents how unmet needs changed between 2004 and 2019/2020 and which individual factors predict unmet need. For Mahdi, it is particularly relevant because it directly connects a macro financing variable to access outcomes in a multi-country European older-adult sample.

**Methods**
- Descriptive trend comparison of unmet need across SHARE waves 1 and 8.
- Multivariable probit regressions for binary unmet-need outcomes.
- Results are reported as average marginal effects for interpretability.
- Models adjust for demographic, socioeconomic, health, and household factors.
- Public health expenditure is included as a country-level predictor.
- The paper estimates country-specific marginal effects for a 20% increase in public health expenditure per capita.
- Statistical significance threshold is 5%; analyses conducted in Stata 17.

**Key findings (for unmet need / access / inequality)**
- Unmet healthcare needs among older Europeans increased substantially between 2004 and 2019/2020 in most countries with available data.
- In 2019/2020, the highest overall prevalence was reported in Greece (27.8%), Romania (20.9%), and Estonia (19.9%).
- The largest increases and highest prevalence were observed for specialist physician services, suggesting persistent barriers to specialist access.
- GP and home-care unmet need were generally lower, but Romania and Hungary stood out for GP access problems.
- Higher public health expenditure significantly reduced the probability of unmet need across all outcomes; the marginal effect for overall unmet need was -0.0495.
- Higher income was protective across most services; compared with the poorest quartile, richer quartiles had lower probabilities of overall, GP, specialist, medicines, and dental unmet need.
- Poor self-reported health and limitations in usual activities increased unmet need for nearly all services.
- A simulated 20% increase in public health expenditure had the largest estimated reductions in Latvia, Cyprus, and Croatia, with smaller effects in already well-funded systems such as Sweden, Switzerland, and Denmark.

**Limitations**
- Countries differ in health-system structure, financing, expectations, and reporting norms, which may moderate the association between expenditure and unmet need.
- System-level organisation, efficiency, waiting-time institutions, and financing details are not fully modelled.
- The unmet-need definition is limited to cost or lack of availability and does not explicitly cover geographical barriers, health literacy, preferences, or waiting times as separate dimensions.
- SHARE data are self-reported and subject to expectation and cultural reporting bias.
- Wave-8 econometric analysis is cross-sectional, so it cannot establish causal effects of public expenditure.
- Broader macroeconomic variables such as GDP growth, labour-market dynamics, and fiscal policy are not included.

**Relevance for Mahdi's thesis**
- This is a strong financing/capacity citation for Mahdi because it links public health expenditure to unmet healthcare need in a European multi-country setting.
- It supports using public expenditure, OOP/private financing, income, and health-status variables as important predictors in panel and ML models.
- The finding that expenditure effects vary by country supports flexible modelling and country-specific heterogeneity rather than assuming one universal slope.
- The specialist-care result is useful for interpreting waiting-time and capacity-related unmet need.
- It reinforces Mahdi's associational framing: public expenditure is predictive and policy-relevant, but causal interpretation requires stronger identification than this design provides.

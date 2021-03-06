# ObsCollection 
One `ObsCollection`

## metadataproperty
One `metadataproperty` block in `ObsCollection`

|NO     |Element CAAML V5   |
| ----- | ----------------- |
|1      |DateTimeReport     |
|1      |operation - name   |

## Observations
One `Observations` block in `ObsCollection`

### bulletin
Multiple `bulletin` blocks in `Observations`

#### metadataproperty
One `metadataproperty` block in `bulletin`
**duplicate**

|NO     |Element CAAML V5   |
| ----- | ----------------- |
|1      |DateTimeReport     |
|1      |Operation - Name   |

#### validtime
One `validtime` block in `bulletin`

|NO     |Element CAAML V5   |Comment                   |
| ----- | ----------------- | ------------------------ |
|1      |beginposition      |DateTime start validity   |
|1      |endposition        |DateTime ende  validity   |

#### srcref
One `secref` with operation name in `bulletin`
**duplicate**

#### locref
Multiple `locref` in `bulletin` with @xlink:href containing the RegionID

#### bulletinresultsof 
One `bulletinresultsof` with `bulletinmeasurements` in `bulletin`

##### dangerratings
One `dangerratings` in `bulletinmeasurements`

###### dangerrating
Multiple `dangerrating` in `dangerratings`

|NO     |Element CAAML V5   |Comment                   |
| ----- | ----------------- | ------------------------ |
|1      |validelevation     |@xlink:href Elevation with Hi or Lo   |
|1      |mainvalue          |Dangerrating Value        |

##### dangerpatterns
One `dangerpatterns` in `bulletinmeasurements`

###### dangerpattern
Multiple `dangerpattern` in `dangerpatterns`

|NO     |Element CAAML V5   |Comment                   |
| ----- | ----------------- | ------------------------ |
|1      |type               |Pattern Type              |

##### avproblems
One `avproblems` in `bulletinmeasurements`

###### avproblem
Multiple `avproblem` in `avproblems`

|NO     |Element CAAML V5   |Comment                   |
| ----- | ----------------- | ------------------------ |
|1      |type               |Problem Type              |
|mult.  |validaspect        |@xlink:href w. Exposition |
|1      |validelevation     |@xlink:href Elevation with Hi or Lo |

##### tendency
One `tendency` in `bulletinmeasurements`

|NO     |Element CAAML V5   |Comment                   |
| ----- | ----------------- | ------------------------ |
|1      |type               |Tendency Type             |
|1      |beginposition      |DateTime start validity   |
|1      |endposition        |DateTime ende  validity   |

*definition tendency types?*

##### avactivityhighlights
One `avactivityhighlights` in `bulletinmeasurements`

##### avactivitycomment
One `avactivitycomment` in `bulletinmeasurements`

##### snowpackstructurecomment
One `snowpackstructurecomment` in `bulletinmeasurements`

##### tendencycomment
One `tendencycomment` in `bulletinmeasurements`

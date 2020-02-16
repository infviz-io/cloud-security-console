import { Component, OnInit } from '@angular/core';
import { CscService } from '../../services/csc.service'

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  awsFound=-1
  azureFound=-1
  awsRecords=[]
  azureRecords=[]

  constructor(
    private cscService: CscService
  ) { }

  ngOnInit(): void {
    this.cscService.getAws().subscribe(
      data=>{
        console.log(data)
        this.awsFound=data['Items'].length
        var tempList=[]
        data['Items'].forEach(element => {
          var tempItem={}
          tempItem=element
          tempItem['Time']=this.convertDate(element['LastObservedAt'])
          tempItem['ShortDesc']=this.textShort(element['Description'])
          tempList.push(tempItem)
        });
        this.awsRecords=tempList
      }
    )
    this.cscService.getAzure().subscribe(
      data=>{
        console.log(data)
        this.azureFound=data['Items'].length
        var tempList=[]
        data['Items'].forEach(element => {
          var tempItem={}
          tempItem=element
          element['Description']=element['Description'].replace('/subscriptions/'+element['SubscriptionId'],'Self')
          tempItem['Time']=this.convertDate(element['LastObservedAt'])
          tempItem['ShortDesc']=this.textShort(element['Description'])
          tempList.push(tempItem)
        });
        this.azureRecords=tempList
      }
    )
  }

convertDate(dtInput){
 //dtInput=dtInput+" GMT"
 let newDate=new Date(dtInput)
 return newDate 
}

textShort(text){
  var output=""
  if (text.length>100){
    output=text.substring(0,100)+"..."
  } else {
    output=text
  }
  return output
}

}

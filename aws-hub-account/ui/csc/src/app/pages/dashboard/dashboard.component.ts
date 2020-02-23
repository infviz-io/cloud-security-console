import { Component, OnInit } from '@angular/core';
import { CscService } from '../../services/csc.service'

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  gcpOn=false
  gcpFound=-1
  awsFound=-1
  azureFound=-1
  awsRecords=[]
  azureRecords=[]
  gcpRecords=[]

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
        this.awsRecords=tempList.reverse()
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
        this.azureRecords=tempList.reverse()
      }
    )
    this.cscService.getGcp().subscribe(
      data=>{
        this.gcpOn=true
        console.log(data)
        this.gcpFound=data['Items'].length
        var tempList=[]
        data['Items'].forEach(element => {
          var tempItem={}
          tempItem=element
          tempItem['Time']=this.convertDate(element['LastObservedAt'])
          tempItem['ShortDesc']=this.textShort(element['Description'])
          tempList.push(tempItem)
        });
        this.gcpRecords=tempList.reverse()
      },
      err=>{
        this.gcpOn=false
        console.log(err)
        console.log("This is normal if GCP is not in use")
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

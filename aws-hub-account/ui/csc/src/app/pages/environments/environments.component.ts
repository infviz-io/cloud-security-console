import { Component, OnInit } from '@angular/core';
import { CscService } from '../../services/csc.service'
import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';

@Component({
  selector: 'app-environments',
  templateUrl: './environments.component.html',
  styleUrls: ['./environments.component.css']
})
export class EnvironmentsComponent implements OnInit {
  envFound=-1
  envRecords=[]
  masterId=""
  azureId=""
  awsId=""

  constructor(
    private cscService: CscService
  ) { }

  ngOnInit(): void {
   this.refreshEnv()
  }

  refreshEnv(){
    this.cscService.getEnv().subscribe(
      data=>{
        console.log(data)
        this.envFound=data['Envs'].length
        this.envRecords=data['Envs']
        data['Envs'].forEach(element => {
          if (element['Status']=="MASTER"){
            this.masterId=element['EnvId']
          }
        });
      }
    )
  }

  addAzure(){
    this.cscService.addCloud('Azure',this.azureId)
    .subscribe(data=>{
      alert("Successfully added Azure Account")
      this.refreshEnv()
      this.azureId=""
    },
    err=>{
      alert("Issue adding Azure Account")
    })
  }

  addAws(){
    this.cscService.addCloud('AWS',this.awsId)
    .subscribe(data=>{
      alert("Successfully added AWS Account")
      this.refreshEnv()
      this.awsId=""
    },
    err=>{
      alert("Issue adding AWS Account")
    })
  }

  removeCloud(select){
    console.log(select)
    if (confirm("Are you sure you want to remove "+select['EnvId']+" from Cloud Security Console?")){
      this.cscService.removeCloud(select['EnvId']).subscribe(data=>{
        this.refreshEnv()
      },err=>{
        this.refreshEnv()
      })
    }

  }

}

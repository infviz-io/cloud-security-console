import { Component } from '@angular/core';
import { Auth } from 'aws-amplify';
import { Router } from '@angular/router';
import { CscService } from './services/csc.service'
import { environment } from '../environments/environment';
import { interval } from 'rxjs';
import { takeWhile } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Cloud Security Console';
  signedIn=false
  authLink="https://"+environment.CognitoDomain+"/login?redirect_uri="+environment.CognitoRedirect+"/&client_id="+environment.CognitoClientId+"&response_type=token"
  activePage="dashboard"

  constructor(
    private cscService: CscService,
    private router:Router
  ){
    interval(500).pipe(takeWhile(()=>!this.signedIn,false)).subscribe(a=>{
      Auth.currentAuthenticatedUser()
      .then(user=>{
        this.signedIn=true
        this.cscService.storeToken(user.signInUserSession.idToken.jwtToken)
      })
      .catch(
        err => {console.log(err)}
      );
    })

  }

  signOut(){
    Auth.signOut()
      .then(user=>{
        this.signedIn=false
      })
  }

  switchPage(page){
    this.activePage=page
    this.router.navigate(['/'+page])
  }

}

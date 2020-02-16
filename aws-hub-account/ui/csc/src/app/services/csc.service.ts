import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CscService {
  cscApi=environment.Api
  idToken;

  constructor(private http: HttpClient) { }

  storeToken(data){
    this.idToken=data
    localStorage.setItem('idToken',this.idToken)
  }

  getAws():Observable<any>{
		const headerOpts=new HttpHeaders().set('Authorization', this.idToken)
		let apiURL=this.cscApi + '/aws'
		return this.http.get(apiURL,{headers:headerOpts})
  }

  getAzure():Observable<any>{
		const headerOpts=new HttpHeaders().set('Authorization', this.idToken)
		let apiURL=this.cscApi + '/azure'
		return this.http.get(apiURL,{headers:headerOpts})
  }

  getEnv():Observable<any>{
		const headerOpts=new HttpHeaders().set('Authorization', this.idToken)
		let apiURL=this.cscApi + '/env'
		return this.http.get(apiURL,{headers:headerOpts})
  }

  addCloud(cloud,envid):Observable<any>{
    var data={"Cloud":cloud,"EnvId":envid}
    const headerOpts=new HttpHeaders().set('Authorization', this.idToken)
		let apiURL=this.cscApi + '/env'
		return this.http.post(apiURL,data,{headers:headerOpts})
  }

  removeCloud(envid):Observable<any>{
    const headerOpts=new HttpHeaders().set('Authorization', this.idToken)
		let apiURL=this.cscApi + '/env/'+envid
		return this.http.delete(apiURL,{headers:headerOpts})
  }
}

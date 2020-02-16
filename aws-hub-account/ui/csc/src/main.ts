import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app/app.module';
import { environment } from './environments/environment';

import Amplify from 'aws-amplify';

const webConfig= {
  region: environment.CognitoRegion,
  userPoolId: environment.CognitoPool,
  userPoolWebClientId: environment.CognitoClientId,
  oauth:{
    domain: environment.CognitoDomain,
    scope:['openid'],
    redirectSignIn: environment.CognitoRedirect+"/",
    redirectSignOut: environment.CognitoRedirect+"/",
    response:'token'
  }
}

Amplify.configure(webConfig)

if (environment.production) {
  enableProdMode();
}

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));

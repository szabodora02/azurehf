param webAppName string
param location string = 'germanywestcentral'
@secure()
param databaseUrl string

// Itt a pontos név, amit a korábbi képeiden láttunk az Azure-ban!
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'ASP-hf-860e'
  location: location
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
    name: 'F1'
    tier: 'Free'
  }
}

resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appSettings: [
        {
          name: 'DATABASE_URL'
          value: databaseUrl
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
      ]
    }
  }
}

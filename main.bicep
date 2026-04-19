// 1. Paraméterek (Ezeket a GitHub Actions fogja átadni)
param webAppName string
param location string = resourceGroup().location
@secure()
param databaseUrl string

// 2. Az App Service Plan (A fizikai szervercsomag) definíciója
// Itt az ingyenes F1-es csomagot állítjuk be, hogy ne fogyjon a kereted!
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'ASP-${webAppName}'
  location: location
  kind: 'linux'
  properties: {
    reserved: true // Ez jelzi, hogy Linuxos szerver
  }
  sku: {
    name: 'F1'
    tier: 'Free'
  }
}

// 3. A Web App (A fényképalbum alkalmazás) definíciója
resource webApp 'Microsoft.Web/sites@2022-03-01' = {
  name: webAppName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12' // Python 3.12 környezet
      appSettings: [
        {
          name: 'DATABASE_URL'
          value: databaseUrl // Biztonságosan injektáljuk az adatbázis URL-t
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true' // Engedélyezi az automatikus buildet Azure-on
        }
      ]
    }
  }
}

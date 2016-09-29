angular.module('notificationApp').
factory('footballFactory', function($http, $cacheFactory, UserConfig) {

    var currentTeam;
    var currentLeagueURL;
    return {

        getLeagues: function() {
            if (!UserConfig.APIkeys.footballAPIkey)
                return Promise.reject("No Football API key");

            return $http({
                method: 'GET',
                cache: true,
                url: 'http://api.football-data.org/v1/competitions',
                headers: {
                    'X-Auth-Token': UserConfig.APIkeys.footballAPIkey
                }
            });
        },

        getLeagueTable: function(response) {
            if (!UserConfig.APIkeys.footballAPIkey)
                return Promise.reject("No Football API key");

            var count = 0;
            while (response.data[count].league != UserConfig.footballLeague)
                count++

                currentLeagueURL = response.data[count]._links.leagueTable.href;

            return $http({
                method: 'GET',
                cache: true,
                url: currentLeagueURL + '',
                headers: {
                    'X-Auth-Token': UserConfig.APIkeys.footballAPIkey
                }
            });
        },

        getFixtures: function() {
            if (!UserConfig.APIkeys.footballAPIkey)
                return Promise.reject("No Football API key");
            return $http({
                method: 'GET',
                cache: true,
                url: currentTeam._links.team.href + '/fixtures',
                headers: {
                    'X-Auth-Token': UserConfig.APIkeys.footballAPIkey
                }
            })

        },

        clearCache: function() {
            $cacheFactory.get('$http').remove(currentLeagueURL);
            $cacheFactory.get('$http').remove(currentTeam._links.team.href + '/fixtures');
        },

        setCurrentTeam: function(team) {
            currentTeam = team;
        },

        getCurrentTeam: function() {
            return currentTeam;
        },

        getCSSClass: function(inputTeam) {
            if (!currentTeam)
                return;
            if (currentTeam.teamName == inputTeam.teamName)
                return "bright"
            else
                return "";
        },

        getNextFixtureString: function(response) {
            var count = 0;
            while (response.data.fixtures[count].status == "FINISHED")
                count++;

            if (response.data.fixtures[count].status == "IN_PLAY")
                return "Playing now";

            return "Next match " + moment(response.data.fixtures[count].date).fromNow();

        }

    }
});

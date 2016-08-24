angular.module('notificationApp.footballFactory', []).
factory('footballFactory', function($http, $cacheFactory, UserConfig) {

    var currentTeam;

    return {
        getLeagueTable: function() {
            return $http({
                method: 'GET',
                cache: true,
                url: 'http://api.football-data.org//v1/competitions/399/leagueTable',
                headers: {
                    'X-Auth-Token': UserConfig.APIkeys.footballAPIkey
                }
            });
        },

        getFixtures: function() {
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
            $cacheFactory.get('$http').remove('http://api.football-data.org//v1/competitions/399/leagueTable');
            $cacheFactory.get('$http').remove(currentTeam._links.team.href + '/fixtures');
        },

        setCurrentTeam: function(team) {
            currentTeam = team;
        },

        getCurrentTeam: function() {
            return currentTeam;
        },

        highlightTeam: function(inputTeam) {
            if (currentTeam == inputTeam)
                return "bright";
            else
                return "";
        },

        getNextFixtureString: function(response) {
            var count = 0;
            while (moment((new Date()).getTime()).isAfter(response.data.fixtures[count].date))
                count++;

            return "Next match " + moment(response.data.fixtures[count].date).fromNow();

        }

    }
});

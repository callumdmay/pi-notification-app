module.exports = function(grunt) {
    //grunt wrapper function
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        clean: {
            clean: ['./build/*', './dist/*']
        },

        eslint: {
            target: ['./app/*.js']
        },

        ngAnnotate: {
            options: {
                singleQuotes: true
            },
            app: {

                files: [{
                    expand: true,
                    src: ['app/**/*.js', '!app/main.js', '!app/app.config.js'],
                    flatten: true,
                    dest: './build/js/',
                    extDot: 'last'
                }]
            }
        },
        concat: {
            js: {
                src: './build/js/*.js',
                flatten: true,
                dest: './build/app.js'
            },

            css: {
                src: './app/**/*.css',
                dest: './dist/styles.css'
            }
        },

        copy: {
            userConfig: {
                src: ['UserConfig.json'],
                dest: './dist/'
            },
            font: {
                expand: true,
                cwd: './app/shared/font',
                src: ['**/*.eot', '**/*.svg', '**/*.ttf', '**/*.woff', '**/*.woff2'],
                dest: './dist/'
            },
            node_modules:{
              expand: true,
              cwd: './node_modules/',
              flatten: true,
              src: ['angular/angular.min.js', 'angular-route/angular-route.min.js',
              'moment/min/moment.min.js', 'bootstrap/dist/css/bootstrap.min.css',
              'angular-ui-swiper/dist/angular-ui-swiper.js'],
              dest: './dist/'
            },
            views: {
              expand: true,
              cwd: './app/',
              src: ['**/*.html', 'app.config.js','main.js'],
              flatten: true,
              dest: './dist/'
            }
        },

        uglify: {
            js: { //target
                src: ['./build/app.js'],
                dest: './dist/app.min.js'
            }
        },

        run: {
            target: {
                exec: 'electron .'
                    // args: ['.']
            }
        }
    });


    //load grunt tasks
    grunt.loadNpmTasks('grunt-eslint');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-ng-annotate');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-run');

    //register grunt default task
    grunt.registerTask('default', ['clean', 'eslint', 'ngAnnotate', 'concat', 'copy', 'uglify', 'run']);
}

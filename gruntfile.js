module.exports = function(grunt) {
  //grunt wrapper function
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    clean: {
      clean: ['./build/*', './dist/*']
    },

    eslint: {
      target: ['./app/**/*.js']
    },

    ngAnnotate: {
      app: {
        files: [{
          src: ['app/app.module.js', 'app/app/config.js', 'app/**/*.js', '!app/main.js'],
          flatten: true,
          dest: './dist/build/app.js',
        }]
      }
    },

    concat: {
      css: {
        src: './app/**/*.css',
        dest: './dist/main.css'
      },

      vendor_css: {
        src: ['./node_modules/bootstrap/dist/css/bootstrap.min.css', './node_modules/animate.css/animate.min.css'],
        flatten: true,
        dest: './dist/vendor.css'
      },

      vendor_js: {
        flatten: true,
        src: ['./node_modules/angular/angular.min.js', './node_modules/angular-route/angular-route.min.js',
          './node_modules/moment/min/moment.min.js'],
        dest: './dist/vendor.min.js'
      },

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

      font_awesome: {
        expand: true,
        cwd: './node_modules/font-awesome',
        src: ['css/**', 'fonts/**'],
        dest: './dist/'
      },

      html: {
        expand: true,
        cwd: './app/',
        src: ['**/*.html'],
        flatten: true,
        dest: './dist/'
      },

      electron: {
        expand: true,
        src: ["app/main.js"],
        flatten: true,
        dest: './dist/'

      }
    },

    uglify: {
      options: {
          sourceMap: true
      },

      js: { //target
        src: ['./dist/build/app.js'],
        dest: './dist/app.min.js'
      }
    },

    run: {
      electron: {
        exec: 'electron .'
      }
    },

    watch: {
      angular: {
        files: ["app/**/*.js", "!app/main.js"],
        tasks: ["ngAnnotate", "uglify"]
      },

      js: {
        files: ["app/main.js"],
        tasks: ["copy:electron"]
      },

      css: {
        files: ["app/**/*.css"],
        tasks: ["concat:css"]
      },

      html: {
        files: ['**/*.html', 'app.config.js', 'main.js'],
        tasks: ["copy:html"]
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
  grunt.loadNpmTasks("grunt-contrib-watch");
  grunt.loadNpmTasks('grunt-run');

  //register grunt default task
  grunt.registerTask('default', ['eslint', 'clean', 'ngAnnotate', 'concat', 'copy', 'uglify']);
  grunt.registerTask('dev', ['default', 'watch']);
  grunt.registerTask('test', ['eslint', 'clean', 'ngAnnotate', 'concat', 'copy', 'uglify']);
  grunt.registerTask('build', ['ngAnnotate', 'concat', 'copy', 'uglify']);
}

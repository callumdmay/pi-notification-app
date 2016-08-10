IF EXIST node_modules GOTO NOWINDIR
   npm install && npm start
:NOWINDIR

npm start

#!/usr/bin/python



import app.configuration

app.configuration.init( verbose = False )



import app.main

def main( ):
   app.main.main( )

if __name__ == "__main__":
   main( )

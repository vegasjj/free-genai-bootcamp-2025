# Ollama container implementation with opea-comps

Q: Could it be possible to use Github Codespaces to mimic a local development environment where
I could test a service from "outside Github Codespaces" e.g. from Windows Terminal?

A: Yes, it is posible. Once the service is up in a local instance of Github Codespaces (using 
Visual Studio Code) the mapped port can be used from a Terminal in the local PC, which in theory
is outside the development environment.


![Ollama service running in docker container](<Ollama container deployed.png>)

![Ollama model 3.2 being pull from repository](<Ollama 3.2 pulled.png>)

![Prompt with Ollama running in Windows Terminal](<Windows Terminal.png>)
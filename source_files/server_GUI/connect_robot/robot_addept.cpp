#include <arpa/inet.h>
#include <iostream>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <sys/types.h>
#include "rapidjson/rapidjson.h"
#include "rapidjson/document.h"
#include "rapidjson/error/en.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include "rapidjson/prettywriter.h"
#include <cstdio>

#define SA struct sockaddr


using namespace rapidjson;


class CommandNetwork{
private:
    int port = 5000;
    char ipAdress[80] = "127.0.0.1"; //default localhost

    int sockfd, connfd;
    uint32_t len;
    struct sockaddr_in servaddr, cli;

    void pars_command(int connfd, char* answer){
        char buff[1024];

        while(true){   
            bzero(buff, 1024);
            read(connfd, buff, sizeof(buff));
            for(int i = 0; i < 1024; ++i) message[i] = buff[i];

            bzero(buff, 1024);
            break;
        }
    }

public:
    char message[1024] = {0};

    CommandNetwork(){
        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        if (sockfd == -1) {
            std::cout << "socket creation failed...\n";
            exit(0);
        }
        else
            std::cout << "Socket successfully created..\n";
        
        bzero(&servaddr, sizeof(servaddr));
   
        servaddr.sin_family = AF_INET;
        servaddr.sin_port = htons(port);

        const char* res = inet_ntop(AF_INET, &servaddr.sin_addr, ipAdress, 80);
        std::cout << "MY IP: " << ipAdress << '\n';

        if ((bind(sockfd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
            std::cout << "socket bind failed...\n";
            exit(0);
        }
        else
            std::cout << "Socket successfully binded..\n";

        if ((listen(sockfd, 5)) != 0) {
            std::cout << "Listen failed...\n";
            exit(0);
            }
        else
            std::cout <<"Server listening..\n";

        len = sizeof(cli);
    }

    ~CommandNetwork(){
        close(sockfd);
    }

    void wait_massage(char* answer = NULL){
        while(true){
            connfd = accept(sockfd,(SA*)&cli, &len);
            if (connfd < 0) {
                std::cout << "server accept failed...\n";
                exit(0);
            }
            else{
                std::cout << "server accept the client...\n";
            }

            pars_command(connfd, answer);
            break;
        }
    }

    void send_back_mess(char* buff){
        write(connfd, buff, sizeof(buff));
    }
};
   
/* BASE JSON CLASS*/
class JSONBase
{
private:
    rapidjson::Document d;
    rapidjson::StringBuffer buffer_json;

public:
    JSONBase(char* json){
        d.Parse(json);
        rapidjson::Writer<rapidjson::StringBuffer> write(buffer_json);

         d.Accept(write);
         std::cout << '\n' <<"I HAVE NEW COMMAND: "<< buffer_json.GetString() << std::endl;
    }
    ~JSONBase(){}

	bool DeserializeDoc(const std::string& s)
    {
	    rapidjson::Document doc;
	    if (!InitDocument(s, doc))
		    return false;
	    return true;
    }

    rapidjson::Value& getDocument(){
        return this->d;
    }

protected:
	bool InitDocument(const std::string & s, rapidjson::Document &doc)
    {
	if (s.empty())
		return false;

	std::string validJson(s);
	return !doc.Parse(validJson.c_str()).HasParseError() ? true : false;    
    }
};


class CommandJson: public JSONBase
{
/*
1. Type Engine - (Left, Right, Tank)
2. Speed
3. Time
*/
public:
	CommandJson(char* json);
	virtual ~CommandJson();			

	virtual std::string getTypeEngine();
	virtual int getSpeed();
	virtual float getTime();

	// Getters/Setters.
    const std::string& TypeEngine() const {return _type_engine;}
    void TypeEngine(std::string& type_engine) {_type_engine = type_engine;}

    int  Speed() const {return _speed;}
    void Speed(int speed) {_speed = speed;}
    
    float Time() const {return _time;}
    void Time(float time) {_time=time;}
    
private:
    std::string _type_engine;
    int _speed;
    float _time;
};

/* Logic Json Modul*/
CommandJson::CommandJson(char* json): JSONBase(json){
}

CommandJson::~CommandJson(){
}

std::string CommandJson::getTypeEngine(){
    const rapidjson::Value& obj = this->getDocument();
    return obj["type_engine"].GetString();
}

float CommandJson::getTime(){
    const rapidjson::Value& obj = this->getDocument();
    return obj["time"].GetFloat();
}

int CommandJson::getSpeed(){
    const rapidjson::Value& obj = this->getDocument();
    return obj["speed"].GetInt();
}


class StackCommand{
private:
    //CommandJson* next_command = NULL;
    CommandJson* this_command = NULL;


public:
    StackCommand(){}
    ~StackCommand(){}

    bool add_new_command(CommandJson* new_command){

        if(this_command == NULL){
            this_command = new_command;
            
            std::cout << '\n' <<"Speed " << this_command->getSpeed() << " Time " << this_command->getTime() << " Type Engine " << this_command->getTypeEngine() << std::endl;

            // try{
            //     std::cout << "Speed " << this_command->getSpeed() << "Time " << this_command->getTime() << "Type Engine " << this_command->getTypeEngine();
            //     /*
            //     Отправка сигнала двигателям
            //     */
            //    throw 10; //Для ошибки
            // }
            // catch(int i){
            //     return false;
            // }

            this_command = NULL;
            return true;
        }
        return false;
    }
};

int main(){
    CommandNetwork* command_send = new CommandNetwork();
    StackCommand* command_stack = new StackCommand();
    
    while (true){
        command_send->wait_massage();

        CommandJson* json_object = new CommandJson(command_send->message);
        if(command_stack->add_new_command(json_object))
        {
            command_send->send_back_mess("0");
        }
        else
        {
            command_send->send_back_mess("1");
        }
        delete json_object;
    }

    delete command_send;
    delete command_stack;
    return 0;
}
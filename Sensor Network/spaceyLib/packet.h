#ifndef __CONSTANTS__
#define __CONSTANTS__
#include "constants.h"
typedef enum {
	CLI_SERV_ACK = 0,
	CLI_SERV_REQ = 1,
	SERV_CLI_DATA = 2
} TPacketType;



class TPacket{
	public:
		TPacketType packetType;
		char seatnum;
		TSeated clusternum;
}

#endif


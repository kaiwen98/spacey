#ifndef __SEAT__
#define __SEAT__

typedef enum{
	NO_CHANGE = 0,
	SEAT_OCCUPIED = 1,
	SEAT_FREE = 2
} TState;

typedef enum{
	IS_SEATED = 1,
	NOT_SEATED = 0
} TSeated;

#endif

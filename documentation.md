Schema of the project architecture 

     
----API-----

+----------+
| Ord mng  |  ->  Database (orders)
|    +     |
|Panel mng |
+----|-----+
|    V     |  ->  Database (accounts), also controlling services and 
|Dispatcher|      core via its syscalls
+----------+
|   Core   |  ->  Database (adb hubs, phones, services etc)
+----------+
|
V
AdbHub -> AdbClient
(HUB mng)  (Physic device mng (phone))
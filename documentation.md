Schema of the project architecture 

     
----API-----

+----------+
| Ord mng  |  ->  Database (orders)
|    +     |
|Panel mng |
+----|-----+
|    V     |
|Dispatcher|  ->  Database (accounts)
+----------+
|   Core   |  ->  Database (adb hubs, phones, services etc)
+----------+
|
V
AdbHub -> AdbClient
(HUB mng)  (Physic device mng (phone))
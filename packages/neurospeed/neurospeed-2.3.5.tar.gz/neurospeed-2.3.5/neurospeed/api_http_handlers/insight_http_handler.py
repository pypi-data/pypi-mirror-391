import copy
from datetime import datetime
from neurospeed.utils.http_service import HttpService
import json
from neurospeed.constants import PROD_API_CONFIG



class Insight_User_Handler:
    """
    Handles user insights by interacting with the API via HTTP requests.
    Provides methods to retrieve various types of insights for a given user.
    """
    def __init__(self, customer_auth_handler, api_config = PROD_API_CONFIG) -> None:
        """
        Initializes the Insight_User_Handler.
        """
        self._insight_api = self.Insight_HttpApi(customer_auth_handler, api_config)
    
    def get_user_insights(self, user_id = None):
        """
        Retrieves basic user insights for a specified user.

        Args:
            user_id (int): The ID of the user whose insights are to be fetched.

        Returns:
            response: The response from the API containing user insights data.
        """
        params = {"user_id":user_id}
        response = self._insight_api.get_user_insights(params)

        return response
    
    def get_user_alltime_insights(self, start_date, end_date, insight_type, boundry, user_id = None):
        """
        Retrieves all-time insights for a user within a specific date range.

        Args:
            user_id (int): The ID of the user.
            start_date (str): The start date for the data range (format: YYYY-MM-DD).
            end_date (str): The end date for the data range (format: YYYY-MM-DD).
            insight_type (str): The type of insight data to be retrieved.
            boundry (str): The time boundary for the data (e.g., 'hour', 'day').

        Returns:
            response: The response from the API containing all-time insights.
        """
        params = {
            "user_id": user_id,
            "start_date":start_date,
            "end_date":end_date,
            "insight_path":insight_type,
            "boundry":boundry
        }
        
        return self._insight_api.get_user_alltime_insights(params)
    
    def get_user_insights_stats(self, daily_date, insight_type, boundry, user_id = None):
        """
        Retrieves statistical insights for a specific day for a user.

        Args:
            user_id (int): The ID of the user.
            daily_date (str): The date for which insights are required (format: YYYY-MM-DD).
            insight_type (str): The type of insight data to be retrieved.
            boundry (str): The time boundary for the data (e.g., 'hour', 'day').

        Returns:
            response: The response from the API containing daily statistical insights.
        """

        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "insight_id":insight_type,
            "time_type":boundry
        }
        
        return self._insight_api.get_user_insights_stats(params)

    def get_user_stress_baseline(self, insight_type,user_id = None):
        params = {
            "user_id": user_id,
            "insight_id": insight_type
        }
        
        return self._insight_api.get_user_stress_baseline(params)
    
    def get_user_daily_stress(self, daily_date, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_user_daily_stress(params)
    
    def get_user_battery(self, daily_date, timezone = None, user_id = None):
        # self._insight_api._headers['Authorization'] = 'Bearer eyJh...'
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_user_battery(params)
    
    def get_user_hourly_insights(self, daily_date, timezone = None, user_id = None):
        
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_user_hourly_insights(params)
    
    def get_user_history_hourly_insights(self, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_user_history_hourly_insights(params)
    
    def get_weekly_stress_average(self, daily_date, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_weekly_stress_average(params)
    
    def get_weekly_stress_change(self, daily_date, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_weekly_stress_change(params)
    
    def get_weekly_stress_index(self, daily_date, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_weekly_stress_index(params)
    
    def get_weekly_best_sleep(self, daily_date, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date
        }
        
        return self._insight_api.get_weekly_best_sleep(params)
    
    def get_weekly_worst_sleep(self, daily_date, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date
        }
        
        return self._insight_api.get_weekly_worst_sleep(params)
    
    def get_weekly_stressful_time(self, daily_date, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_weekly_stressful_time(params)
    
    def get_weekly_quiet_time(self, daily_date, timezone = None, user_id = None):
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "local_timezone":timezone
        }
        
        return self._insight_api.get_weekly_quiet_time(params)
    
    def get_first_day_of_the_week(self, user_id = None):
        params = {
            "user_id": user_id
        }
        return self._insight_api.get_first_day_of_the_week(params)
    
    def set_first_day_of_the_week(self, first_day_of_week, user_id = None):
        params = {
            "user_id": user_id,
            "first_day_of_week": first_day_of_week
        }
        return self._insight_api.set_first_day_of_the_week(params)
    
    def get_calendar_stress_graph(self, todays_date, user_id = None):
        params = {
            "user_id": user_id,
            "todays_date": todays_date
        }
        return self._insight_api.get_calendar_stress_graph(params)
    
    def get_dates_of_last_6_month_without_stress(self, todays_date, user_id = None):
        params = {
            "user_id": user_id,
            "todays_date": todays_date
        }
        return self._insight_api.get_dates_of_last_6_month_without_stress(params)
    
    def get_dates_of_last_6_month_with_stress(self, todays_date, user_id = None):
        params = {
            "user_id": user_id,
            "todays_date": todays_date
        }
        return self._insight_api.get_dates_of_last_6_month_with_stress(params)
    
    def calculate_daily_stress_for_6_month(self, todays_date, user_id = None):
        params = {
            "user_id": user_id,
            "todays_date": todays_date
        }
        return self._insight_api.calculate_daily_stress_for_6_month(params)
    
    def get_user_all_insights_stats(self, daily_date, insight_type, boundry, user_id = None):
        """
        Retrieves all available statistical insights for a specific day for a user.

        Args:
            user_id (int): The ID of the user.
            daily_date (str): The date for which insights are required (format: YYYY-MM-DD).
            insight_type (str): The type of insight data to be retrieved.
            boundry (str): The time boundary for the data (e.g., 'hour', 'day').

        Returns:
            response: The response from the API containing all daily statistical insights.
        """
        params = {
            "user_id": user_id,
            "daily_date":daily_date,
            "insight_id":insight_type,
            "time_type":boundry
        }
        
        return self._insight_api.get_user_all_insights_stats(params)

    
    
    class Insight_HttpApi:
        """
        A helper class responsible for making HTTP requests to the API endpoints
        related to user insights.
        """
        def __init__(self,auth_handler, api_config = PROD_API_CONFIG) -> None:
            """
            Initializes the Insight_HttpApi.
            """
            self._insight_endpoint = '/users/settings'
            self._http_service = HttpService(auth_handler, api_config=api_config)
            self._http_service.set_headers(auth_handler.get_access_token())
        
        def get_user_insights(self,params):
            """
            Sends a GET request to retrieve user insights.

            Args:
                params (dict): Parameters for the API request.

            Returns:
                response: The response from the API.
            """
            endpoint = self._insight_endpoint + "/insights"
            response = self._http_service.GET_request(endpoint,params,self.get_headers())
            return response
        
        def get_user_alltime_insights(self,params):
            """
            Sends a POST request to retrieve all-time user insights.

            Args:
                params (dict): Parameters for the API request.

            Returns:
                response: The response from the API.
            """
            endpoint = self._insight_endpoint+"/insights/alltime"
            response = self._http_service.POST_request(endpoint,params,self.get_headers())
            return response

        def get_user_insights_stats(self,params):
            """
            Sends a POST request to retrieve user insights statistics for a specific day.

            Args:
                params (dict): Parameters for the API request.

            Returns:
                response: The response from the API.
            """
            endpoint = self._insight_endpoint+"/insights/daily_stats"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_user_stress_baseline(self,params):
            endpoint = self._insight_endpoint+"/insights/stress_baseline"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_user_daily_stress(self,params):
            endpoint = self._insight_endpoint+"/insights/daily_stress"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_user_battery(self,params):
            endpoint = self._insight_endpoint+"/insights/battery"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_user_hourly_insights(self,params):
            endpoint = self._insight_endpoint+"/insights/hourly_insights"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_user_history_hourly_insights(self,params):
            endpoint = self._insight_endpoint+"/insights/history_hourly_insights"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_stress_average(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_stress_average"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_stress_change(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_stress_change"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_stress_index(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_stress_index"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_best_sleep(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_best_sleep"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_worst_sleep(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_worst_sleep"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_stressful_time(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_stressful_time"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_weekly_quiet_time(self,params):
            endpoint = self._insight_endpoint+"/insights/weekly_quiet_time"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_first_day_of_the_week(self, params):
            endpoint = self._insight_endpoint+"/insights/weekly_first_day_of_week"
            response = self._http_service.GET_request(endpoint,params,headers=self.get_headers())
            return response
        
        def set_first_day_of_the_week(self, params):
            endpoint = self._insight_endpoint+"/insights/weekly_first_day_of_week"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_calendar_stress_graph(self, params):
            endpoint = self._insight_endpoint+"/insights/calendar/calendar_stress_graph"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_dates_of_last_6_month_without_stress(self, params):
            endpoint = self._insight_endpoint+"/insights/calendar/dates_of_last_6_month_without_stress"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_dates_of_last_6_month_with_stress(self, params):
            endpoint = self._insight_endpoint+"/insights/calendar/dates_of_last_6_month_with_stress"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def calculate_daily_stress_for_6_month(self, params):
            endpoint = self._insight_endpoint+"/insights/calendar/calculate_daily_stress_for_6_month"
            response = self._http_service.POST_request(endpoint,payload=params,headers=self.get_headers())
            return response
        
        def get_user_all_insights_stats(self,params):
            """
            Sends a POST request to retrieve all user insights statistics.

            Args:
                params (dict): Parameters for the API request.

            Returns:
                response: The response from the API.
            """
            endpoint = self._insight_endpoint+"/insights/all_daily_stats"
            response = self._http_service.POST_request(endpoint,params,self.get_headers())
            return response
        
        def get_headers(self):
            """
            Retrieves a copy of the authorization headers.

            Returns:
                dict: A deep copy of the authorization headers.
            """
            return copy.deepcopy(self._http_service.get_and_update_headers())
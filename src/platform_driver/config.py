from datetime import timedelta
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


latest_config_version = 2

class GroupConfig(BaseModel):
    minimum_polling_interval: float = 1.0
    start_offset: timedelta = timedelta(seconds=0.0)
    poll_scheduler_class_name: str = 'StaticCyclicPollScheduler'
    poll_scheduler_module: str = 'platform_driver.poll_scheduler'
    poll_scheduler_configs: BaseModel | None = None
    parallel_subgroups: bool = False

    @classmethod
    @field_validator('start_offset', mode='before')
    def _make_start_offset(cls, v):
        return timedelta(seconds=v)


class PlatformDriverConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True, populate_by_name=True)
    config_version: int = latest_config_version
    allow_duplicate_remotes: bool = False
    allow_no_lock_write: bool = False  # TODO: Alias with "require_reservation_to_write"?
    allow_reschedule: bool = True
    # TODO: Is there a better default for breadth_first_base besides "devices" or "points",
    #  since point names are still keys in the dict? Maybe just "breadth" or something?
    #  This will actually be organized (in all/multi) as device/building/campus: {point1: val1, point2: val2}
    breadth_first_base: str = 'points'
    default_polling_interval: float = 60
    depth_first_base: str = 'devices'
    groups: dict[str, GroupConfig] = {}
    group_offset_interval: float = 0.0
    max_concurrent_publishes: int = 10000
    max_open_sockets: int | None = None
    minimum_polling_interval: float = Field(default=0.02, alias='driver_scrape_interval')
    poll_scheduler_class_name: str = 'StaticCyclicPollScheduler'
    poll_scheduler_configs: BaseModel | None = None
    poll_scheduler_module: str = 'platform_driver.poll_scheduler'
    publish_single_depth: bool = Field(default=False, alias='publish_depth_first_single')
    publish_single_breadth: bool = Field(default=False, alias='publish_breadth_first_single')
    publish_all_breadth: bool = Field(default=False, alias='publish_breadth_first_all')
    publish_multi_breadth: bool = Field(default=False, alias='publish_breadth_first_multi')
    remote_heartbeat_interval: float = 60.0
    reservation_preempt_grace_time: float = 60.0
    reservation_publish_interval: float = 60.0
    reservation_required_for_write: bool = False
    scalability_test: bool = False
    scalability_test_iterations: int = 3
    timezone: str = 'UTC'  # TODO: This needs integration (is is currently used in creating register metadata). The
                           #  driver has traditionally configured timezones at the device level, but these are not used
                           #  to create the timestamps that accompany them. They should really match
                           #  and (at least by default?) be global.

    @model_validator(mode='after')
    def _set_default_group(self):
        if 'default' not in self.groups:
            self.groups['default'] = GroupConfig(
                minimum_interval=self.minimum_polling_interval,
                poll_scheduler_class_name=self.poll_scheduler_class_name,
                poll_scheduler_module=self.poll_scheduler_module,
                start_offset=self.group_offset_interval,
                parallel_subbgroups=True
            )

class PlatformDriverConfigV2(PlatformDriverConfig):
    config_version: int = 2
    publish_all_depth: bool = Field(default=False, alias='publish_depth_first_all')
    publish_multi_depth: bool = Field(default=True, alias='publish_depth_first_multi')


class PlatformDriverConfigV1(PlatformDriverConfig):
    config_version: int = 1
    publish_all_depth: bool = Field(default=True, alias='publish_depth_first_all')
    publish_multi_depth: bool = Field(default=False, alias='publish_depth_first_multi')

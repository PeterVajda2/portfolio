from .models import Smartkpi, Smartkpiorderkeyvaluedata, Smartkpimachinemessagedata, Smartkpiprocessfloatdata, Shiftcalendar, TempSmartkpicvsproductiontargetdetail, Tb_fp09_alarms, Smartkpivalues, Smartkpimachinestatusdata, Tb_fp09_alarmstext, TbFp09CtSt135, Tb_fp09_qd
from fp09.models import TbFp09Qd
from shift_factor.models import OBC_Linka1, Productioncounts
from strama.models import TbBcMasterparts, TbPpAxisparameters, TbPpPartparameters, TbStramaQd
class MyDBRouter(object):

    def db_for_read(self, model, **hints):
        if model in [Smartkpi, Smartkpiorderkeyvaluedata, Smartkpimachinemessagedata, Smartkpiprocessfloatdata, Shiftcalendar, TempSmartkpicvsproductiontargetdetail, Smartkpivalues, Smartkpimachinestatusdata]:
            return 'backup_twx'
        elif model in [Tb_fp09_alarms, TbFp09Qd]:
            return 'jirkal'
        elif model in [Tb_fp09_alarmstext, TbFp09CtSt135, Tb_fp09_qd, ]:
            return 'jirkal_111'
        elif model in [OBC_Linka1, Productioncounts]:
            return 'provozni_data'
        elif model in [TbBcMasterparts, TbPpAxisparameters, TbPpPartparameters, TbStramaQd]:
            return 'strama_test'
        else:
            return 'default'
        return None

    
    def db_for_write(self, model, **hints):
        if model in [Smartkpi, Smartkpiorderkeyvaluedata, Smartkpimachinemessagedata, Smartkpiprocessfloatdata, Shiftcalendar, TempSmartkpicvsproductiontargetdetail, Smartkpivalues, Smartkpimachinestatusdata]:
            return 'backup_twx'
        elif model in [Tb_fp09_alarms]:
            return 'jirkal'
        elif model in [Tb_fp09_alarmstext, TbFp09CtSt135, Tb_fp09_qd]:
            return 'jirkal_111'
        elif model in [OBC_Linka1, Productioncounts]:
            return 'provozni_data'
        elif model in [TbBcMasterparts, TbPpAxisparameters, TbPpPartparameters, TbStramaQd]:
            return 'strama_test'   
        else:
            return 'default'
        return None
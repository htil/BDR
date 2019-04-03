// Generated by gencpp from file bebop_msgs/CommonRunStateRunIdChanged.msg
// DO NOT EDIT!


#ifndef BEBOP_MSGS_MESSAGE_COMMONRUNSTATERUNIDCHANGED_H
#define BEBOP_MSGS_MESSAGE_COMMONRUNSTATERUNIDCHANGED_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <std_msgs/Header.h>

namespace bebop_msgs
{
template <class ContainerAllocator>
struct CommonRunStateRunIdChanged_
{
  typedef CommonRunStateRunIdChanged_<ContainerAllocator> Type;

  CommonRunStateRunIdChanged_()
    : header()
    , runId()  {
    }
  CommonRunStateRunIdChanged_(const ContainerAllocator& _alloc)
    : header(_alloc)
    , runId(_alloc)  {
  (void)_alloc;
    }



   typedef  ::std_msgs::Header_<ContainerAllocator>  _header_type;
  _header_type header;

   typedef std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other >  _runId_type;
  _runId_type runId;





  typedef boost::shared_ptr< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> const> ConstPtr;

}; // struct CommonRunStateRunIdChanged_

typedef ::bebop_msgs::CommonRunStateRunIdChanged_<std::allocator<void> > CommonRunStateRunIdChanged;

typedef boost::shared_ptr< ::bebop_msgs::CommonRunStateRunIdChanged > CommonRunStateRunIdChangedPtr;
typedef boost::shared_ptr< ::bebop_msgs::CommonRunStateRunIdChanged const> CommonRunStateRunIdChangedConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >::stream(s, "", v);
return s;
}

} // namespace bebop_msgs

namespace ros
{
namespace message_traits
{



// BOOLTRAITS {'IsFixedSize': False, 'IsMessage': True, 'HasHeader': True}
// {'std_msgs': ['/opt/ros/kinetic/share/std_msgs/cmake/../msg'], 'bebop_msgs': ['/home/htil/Documents/bdr-cfc8271e0834a2481b4018a760c212cd3ca15cc9/bdr_ws/src/bebop_autonomy/bebop_msgs/msg']}

// !!!!!!!!!!! ['__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_parsed_fields', 'constants', 'fields', 'full_name', 'has_header', 'header_present', 'names', 'package', 'parsed_fields', 'short_name', 'text', 'types']




template <class ContainerAllocator>
struct IsFixedSize< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct IsMessage< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> const>
  : TrueType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
{
  static const char* value()
  {
    return "b7ac1570fb76100e35b4cf4959b304cb";
  }

  static const char* value(const ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xb7ac1570fb76100eULL;
  static const uint64_t static_value2 = 0x35b4cf4959b304cbULL;
};

template<class ContainerAllocator>
struct DataType< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
{
  static const char* value()
  {
    return "bebop_msgs/CommonRunStateRunIdChanged";
  }

  static const char* value(const ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
{
  static const char* value()
  {
    return "# CommonRunStateRunIdChanged\n\
# auto-generated from up stream XML files at\n\
#   github.com/Parrot-Developers/libARCommands/tree/master/Xml\n\
# To check upstream commit hash, refer to last_build_info file\n\
# Do not modify this file by hand. Check scripts/meta folder for generator files.\n\
#\n\
# SDK Comment: Current run id.\\n A run id is uniquely identifying a run or a flight.\\n For each run is generated on the drone a file which can be used by Academy to sum up the run.\\n Also, each medias taken during a run has a filename containing the run id.\n\
\n\
Header header\n\
\n\
# Id of the run\n\
string runId\n\
\n\
================================================================================\n\
MSG: std_msgs/Header\n\
# Standard metadata for higher-level stamped data types.\n\
# This is generally used to communicate timestamped data \n\
# in a particular coordinate frame.\n\
# \n\
# sequence ID: consecutively increasing ID \n\
uint32 seq\n\
#Two-integer timestamp that is expressed as:\n\
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')\n\
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')\n\
# time-handling sugar is provided by the client library\n\
time stamp\n\
#Frame this data is associated with\n\
# 0: no frame\n\
# 1: global frame\n\
string frame_id\n\
";
  }

  static const char* value(const ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.header);
      stream.next(m.runId);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct CommonRunStateRunIdChanged_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::bebop_msgs::CommonRunStateRunIdChanged_<ContainerAllocator>& v)
  {
    s << indent << "header: ";
    s << std::endl;
    Printer< ::std_msgs::Header_<ContainerAllocator> >::stream(s, indent + "  ", v.header);
    s << indent << "runId: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other > >::stream(s, indent + "  ", v.runId);
  }
};

} // namespace message_operations
} // namespace ros

#endif // BEBOP_MSGS_MESSAGE_COMMONRUNSTATERUNIDCHANGED_H
